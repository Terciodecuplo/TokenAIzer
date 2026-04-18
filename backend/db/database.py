import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".tokenAIzer" / "db.sqlite"


def get_db_path() -> Path:
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL DEFAULT 0,
                output_tokens INTEGER NOT NULL DEFAULT 0,
                thinking_tokens INTEGER NOT NULL DEFAULT 0,
                cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
                cache_read_tokens INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL CHECK(source IN ('proxy', 'manual'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS model_pricing (
                model TEXT PRIMARY KEY,
                input_price_per_million REAL NOT NULL DEFAULT 0,
                output_price_per_million REAL NOT NULL DEFAULT 0,
                cache_creation_price_per_million REAL NOT NULL DEFAULT 0,
                cache_read_price_per_million REAL NOT NULL DEFAULT 0,
                currency TEXT NOT NULL DEFAULT 'USD',
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
