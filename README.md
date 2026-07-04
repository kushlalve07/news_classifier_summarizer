# 📰 Samachar — Personalised News Aggregator

> Your personalised Indian news feed, powered by LLaMA 3.1 via Groq API.

![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20React%20%2B%20Vite-blue)
![Database](https://img.shields.io/badge/database-Neon%20Postgres-green)
![AI](https://img.shields.io/badge/AI-Groq%20LLaMA%203.1-orange)
![Deploy](https://img.shields.io/badge/deploy-Render%20%2B%20Vercel-purple)

---

## 🌐 Live Demo

- **Frontend:** [news-app-frontend-jet-ten.vercel.app](https://news-app-frontend-jet-ten.vercel.app)
- **Backend API Docs:** [news-app-backend-wczm.onrender.com/docs](https://news-app-backend-wczm.onrender.com/docs)

---

## 📌 What It Does

InBrief aggregates live news from 30+ Indian RSS sources, classifies each article into a category, generates a 2-line AI summary, and serves a personalised feed based on each user's topic and city preferences — all within seconds thanks to a shared article cache.

- 🔐 User registration and login with bcrypt password hashing
- 🗂️ Personalised topic selection (Sports, Tech, Business, Politics, Entertainment, World, Science)
- 📍 City-based local news (Mumbai, Delhi, Bangalore, and more)
- ✍️ AI-generated 2-line summaries via Groq (LLaMA 3.1 8B Instant)
- ⚡ Shared Postgres cache — Groq runs once per 3 hours for all users
- 🔍 Live search across headlines and sources
- 📰 Category tabs with article count badges
- 🔄 Manual feed refresh with cache status indicator

---

## 🏗️ Architecture

```
Frontend (React + Vite)          Backend (FastAPI)           Database (Neon Postgres)
────────────────────────         ──────────────────          ───────────────────────
LoginPage                        POST /auth/register    →    users
RegisterPage (with prefs)        POST /auth/login       →    users
DashboardPage                    POST /preferences/save →    preferences
  ├── TabBar                     GET  /preferences/:id  →    preferences
  ├── SearchBar                  POST /feed             →    article_cache
  ├── NewsCard                   POST /admin/refresh    →    article_cache
  └── PreferencesModal           GET  /health                cache_meta

                                 Services
                                 ├── rss_service.py      ← feedparser, 30+ feeds
                                 ├── groq_service.py     ← LLaMA 3.1 via Groq API
                                 ├── ranking_service.py  ← preference-based sorting
                                 └── cache_service.py    ← shared 3hr cache logic
```

---

## 🗄️ Database Schema

```sql
users          — user_id, username, password_hash, created_at
preferences    — pref_id, user_id, topics, sources, city, updated_at
article_cache  — article_id, title, summary, link (UNIQUE), source,
                 category, is_regional, published, city, cached_at
cache_meta     — meta_id, last_refreshed
```

---

## 📡 RSS Sources

| Category | Sources |
|----------|---------|
| Sports | TOI Sports, TOI Cricket |
| Technology | TOI Gadgets, TOI Science |
| Business | TOI Business |
| Entertainment | TOI Entertainment, TOI Life & Style |
| World | TOI World |
| India | TOI India |
| Environment | TOI Environment |
| Regional | HT City feeds, DNA city feeds, The Hindu Chennai, Siasat, Telangana Today, and more |

---

## ⚡ Caching Strategy

Instead of calling Groq per user per login, InBrief uses a **shared article cache**:

```
Every 3 hours:
  Fetch ALL categories + ALL cities from RSS
  Classify + summarise each article via Groq (once)
  Store in Neon article_cache table

Per user request:
  Filter cached articles by user's topics + city
  Rank preferred topics first
  Return instantly — zero Groq calls
```

This reduces LLM API usage by ~90% compared to per-user processing.

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neon Postgres account (free at neon.tech)
- Groq API key (free at console.groq.com)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in DATABASE_URL and GROQ_API_KEY in .env

uvicorn main:app --reload
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install

# Create .env.local file
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
# App runs at http://localhost:5173
```

---

## 🌍 Deployment

| Service | Platform | Config |
|---------|----------|--------|
| Frontend | Vercel | Root: `frontend`, auto-detects Vite |
| Backend | Render | Root: `backend`, start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Database | Neon | Serverless Postgres, free tier |
| Cache Refresh | Render Cron | `python refresh_job.py` every 3 hours (`0 */3 * * *`) |

---

## 📁 Project Structure

```
inbrief/
├── backend/
│   ├── main.py                 # FastAPI app + all routes
│   ├── config.py               # env variable loader
│   ├── refresh_job.py          # standalone cron script
│   ├── requirements.txt
│   ├── database/
│   │   └── db.py               # Neon Postgres queries
│   └── services/
│       ├── rss_service.py      # RSS fetching + parsing
│       ├── groq_service.py     # Groq API + classify/summarise
│       ├── ranking_service.py  # preference-based article ranking
│       └── cache_service.py    # shared cache refresh logic
│
└── frontend/
    ├── vercel.json             # SPA routing fix
    ├── .env.production         # VITE_API_URL for live deploy
    └── src/
        ├── App.jsx             # routing + auth state
        ├── services/
        │   └── api.js          # all backend API calls
        ├── pages/
        │   ├── LoginPage.jsx   # login + register forms
        │   └── DashboardPage.jsx
        └── components/
            ├── NewsCard.jsx
            └── PreferencesModal.jsx
```

---

## 🔧 Environment Variables

### Backend `.env`
```
DATABASE_URL=postgresql://...@....neon.tech/neondb?sslmode=require
GROQ_API_KEY=gsk_...
```

### Frontend `.env.production`
```
VITE_API_URL=https://your-render-url.onrender.com
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React Router v6 |
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | Neon Postgres (serverless), psycopg2 |
| AI/LLM | Groq API — LLaMA 3.1 8B Instant |
| RSS Parsing | feedparser |
| Auth | bcrypt password hashing |
| Deployment | Vercel (frontend), Render (backend) |

---

## 📄 License

MIT — feel free to fork and build on top of this.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) for the blazing fast LLaMA inference API
- [Neon](https://neon.tech) for serverless Postgres
- [Times of India](https://timesofindia.com), [Hindustan Times](https://hindustantimes.com), [The Hindu](https://thehindu.com), [Siasat](https://siasat.com) and other publishers for their public RSS feeds
- Built with assistance from Claude (Anthropic)
