import psycopg2
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            pref_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            topics TEXT,
            sources TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def create_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username) VALUES (%s) RETURNING user_id",
        (username,)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def save_preferences(user_id, topics, sources, city):
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if preferences already exist for this user
    cur.execute(
        "SELECT pref_id FROM preferences WHERE user_id = %s",
        (user_id,)
    )
    existing = cur.fetchone()
    
    if existing:
        cur.execute("""
            UPDATE preferences 
            SET topics = %s, sources = %s, updated_at = CURRENT_TIMESTAMP, city = %s
            WHERE user_id = %s
        """, (",".join(topics), ",".join(sources), city, user_id))
    else:
        cur.execute("""
            INSERT INTO preferences (user_id, topics, sources, city)
            VALUES (%s, %s, %s, %s)
        """, (user_id, ",".join(topics), ",".join(sources), city))
    
    conn.commit()
    cur.close()
    conn.close()

def get_preferences(user_id):
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
    
    topics = row[0].split(",") if row[0] else []
    sources = row[1].split(",") if row[1] else []
    city = row[2]
    return {"topics": topics, "sources": sources, "city": city}