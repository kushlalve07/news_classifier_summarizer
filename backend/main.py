from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List
import re

from database.db import (
    create_tables, get_user, create_user,
    save_preferences, get_preferences,
    get_articles_from_cache, cache_needs_refresh
)

from services.rss_service import fetch_articles
from services.groq_service import classify_and_summarize
from services.cache_service import refresh_cache
from services.ranking_service import rank_articles
import time

app = FastAPI()

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

# ── Pydantic models (request/response shapes) ─────────
class RegisterRequest(BaseModel):
    username: str
    password: str

    @validator("username")
    def validate_username(cls, v):
        v = v.strip()
        if len(v) < 7:
            raise ValueError("Username must be at least 7 characters")
        if not v.islower():
            raise ValueError("Username must be all lowercase")
        if " " in v:
            raise ValueError("Username must not contain spaces")
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError("Only lowercase letters, numbers, underscores allowed")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class PreferencesRequest(BaseModel):
    user_id: int
    topics: List[str]
    city: Optional[str] = None

class FeedRequest(BaseModel):
    user_id: int

# ── Auth routes ───────────────────────────────────────
@app.post("/auth/register")
def register(req: RegisterRequest):
    existing = get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user_id = create_user(req.username, req.password)
    return {"user_id": user_id, "username": req.username}

@app.post("/auth/login")
def login(req: LoginRequest):
    user = get_user(req.username.strip())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # user[2] is password_hash
    from database.db import verify_password
    if not verify_password(req.password, user[2]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {"user_id": user[0], "username": user[1]}

# ── Preferences routes ────────────────────────────────
@app.post("/preferences/save")
def save_prefs(req: PreferencesRequest):
    save_preferences(req.user_id, req.topics, [], req.city)
    return {"success": True}

@app.get("/preferences/{user_id}")
def get_prefs(user_id: int):
    prefs = get_preferences(user_id)
    if not prefs:
        return {"topics": [], "city": None}
    return prefs

# ── Feed route ────────────────────────────────────────
@app.post("/feed")
def get_feed(request_data: FeedRequest): # Adjust parameters to match your setup
    # 1. Fetch user preferences
    prefs = get_preferences(request_data.user_id)
    if not prefs or not prefs["topics"]:
        return {"status": "ok", "articles": []}
    
    # 2. STRICTLY pull from your Neon cache table
    # Do NOT run live Groq updates inside this endpoint!
    cached_articles = get_articles_from_cache(topics=prefs["topics"], city=prefs["city"])
    
    return {"status": "ok", "articles": cached_articles}

@app.post("/admin/refresh-cache")
def force_refresh():
    """Manually trigger a cache refresh. Useful for testing."""
    count = refresh_cache()
    return {"success": True, "articles_cached": count}