import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("messages.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)

def save_message(phone, direction, body, whatsapp_message_id=""):
    with get_connection() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO messages
               (phone, direction, body, whatsapp_message_id)
               VALUES (?, ?, ?, ?)""",
            (phone, direction, body, whatsapp_message_id),
        )

def get_recent_messages(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, phone, direction, body, created_at
               FROM messages ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
