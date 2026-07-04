import psycopg2
import bcrypt
from config import DATABASE_URL
import datetime
from datetime import timezone

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            pref_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            topics TEXT,
            sources TEXT,
            city TEXT DEFAULT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_user(username: str, password: str) -> int:
    print(f"Creating a user with username : {username} and password : {password}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id",
        (username, hash_password(password))
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user(username: str):
    print(f"Getting a user with username : {username}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username, password_hash FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def save_preferences(user_id, topics, sources, city=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT pref_id FROM preferences WHERE user_id = %s",
        (user_id,)
    )
    existing = cur.fetchone()
    if existing:
        print(f"There are existing preferences : {existing}. Can edit them now.")
        cur.execute("""
            UPDATE preferences
            SET topics = %s, sources = %s, city = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """, (",".join(topics), ",".join(sources), city, user_id))
    else:
        print("No existing preferences. Adding them now.")
        cur.execute("""
            INSERT INTO preferences (user_id, topics, sources, city)
            VALUES (%s, %s, %s, %s)
        """, (user_id, ",".join(topics), ",".join(sources), city))
    conn.commit()
    cur.close()
    conn.close()

def get_preferences(user_id):
    print(f"Getting preferences for user ID: {user_id}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT topics, sources, city FROM preferences WHERE user_id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "topics": row[0].split(",") if row[0] else [],
        "sources": row[1].split(",") if row[1] else [],
        "city": row[2]
    }

def save_articles_to_cache(articles: list):
    """
    Insert processed articles into shared cache.
    Uses INSERT ... ON CONFLICT DO NOTHING to skip duplicates.
    """
    conn = get_connection()
    cur = conn.cursor()

    for a in articles:
        cur.execute("""
            INSERT INTO article_cache 
                (title, summary, link, source, category, is_regional, published, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING
        """, (
            a["title"], a["summary"], a["link"],
            a["source"], a["category"], a["is_regional"],
            a["published"], a.get("city")
        ))

    conn.commit()
    cur.close()
    conn.close()

def get_articles_from_cache(topics: list, city: str = None) -> list:
    """
    Fetch cached articles matching user's topic preferences.
    Optionally includes regional articles for their city.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Build category filter
    # topics is e.g. ["Sports", "Technology"]
    placeholders = ",".join(["%s"] * len(topics))

    if city:
        cur.execute(f"""
            SELECT title, summary, link, source, category, 
                   is_regional, published, city
            FROM article_cache
            WHERE category IN ({placeholders})
               OR (is_regional = TRUE AND city = %s)
            ORDER BY cached_at DESC
        """, (*topics, city))
    else:
        cur.execute(f"""
            SELECT title, summary, link, source, category,
                   is_regional, published, city
            FROM article_cache
            WHERE category IN ({placeholders})
            ORDER BY cached_at DESC
        """, tuple(topics))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "title": row[0],
            "summary": row[1],
            "link": row[2],
            "source": row[3],
            "category": row[4],
            "is_regional": row[5],
            "published": row[6],
            "city": row[7]
        }
        for row in rows
    ]

def get_last_refresh_time():
    """Returns datetime of last cache refresh, or None if never refreshed."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_refreshed FROM cache_meta ORDER BY meta_id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def update_refresh_time():
    """Record that a refresh just happened."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO cache_meta (last_refreshed) VALUES (CURRENT_TIMESTAMP)")
    conn.commit()
    cur.close()
    conn.close()

def clear_stale_articles():
    """Delete articles older than 72 hours from cache."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM article_cache 
        WHERE cached_at < CURRENT_TIMESTAMP - INTERVAL '72 hours'
    """)
    conn.commit()
    cur.close()
    conn.close()

def cache_needs_refresh(max_age_hours: int = 3) -> bool:
    """Returns True if cache is stale or has never been populated."""
    last = get_last_refresh_time()
    if not last:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
        
    age_hours = (datetime.datetime.now(timezone.utc) - last).total_seconds() / 3600
    return age_hours > max_age_hours