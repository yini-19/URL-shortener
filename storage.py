import sqlite3
from datetime import datetime, timezone

DB_PATH = "shortener.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            creator_email TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0,
            expires_at TIMESTAMP
            )
    """)

    conn.commit()
    conn.close()

def save_link(code: str, original_url: str, creator_email: str, expires_at=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO links (code, original_url, creator_email, created_at, clicks, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
        (code, original_url, creator_email, datetime.now(timezone.utc), 0, expires_at),
    )
    conn.commit()
    conn.close()

def get_link(code: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM links WHERE code = ?", (code,)
    ).fetchone()
    conn.close()
    return row

def increment_clicks(code: str):
    conn = get_connection()
    conn.execute(
        "UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,)
    )
    conn.commit()
    conn.close()

def code_exist(code: str) -> bool:
    return get_link(code) is not None
