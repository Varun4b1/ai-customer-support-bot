"""
database.py
------------
SQLite database for:
  1. Chat history — every question + answer, tagged by user
  2. File registry — tracks which files have been uploaded
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("./support_bot.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Call once at startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            uploaded_by TEXT NOT NULL,
            chunk_count INTEGER DEFAULT 0,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables ready.")


def save_chat(user_email: str, session_id: str, question: str, answer: str, sources: str):
    conn = get_connection()
    conn.execute(
        """INSERT INTO chat_history (user_email, session_id, question, answer, sources, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_email, session_id, question, answer, sources, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_chat_history(user_email: str, limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        """SELECT question, answer, sources, created_at FROM chat_history
           WHERE user_email = ? ORDER BY created_at DESC LIMIT ?""",
        (user_email, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def register_file(filename: str, uploaded_by: str, chunk_count: int):
    conn = get_connection()
    conn.execute(
        """INSERT INTO files (filename, uploaded_by, chunk_count, uploaded_at)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(filename) DO UPDATE SET
             chunk_count=excluded.chunk_count,
             uploaded_at=excluded.uploaded_at""",
        (filename, uploaded_by, chunk_count, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def list_files():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM files ORDER BY uploaded_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]