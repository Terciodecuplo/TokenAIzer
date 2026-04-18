import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Anthropic list prices as of 2026-04-18 (USD per million tokens)
_DEFAULT_PRICING = [
    {
        "model": "claude-opus-4-6",
        "input_price_per_million": 15.0,
        "output_price_per_million": 75.0,
        "cache_creation_price_per_million": 18.75,
        "cache_read_price_per_million": 1.50,
    },
    {
        "model": "claude-sonnet-4-6",
        "input_price_per_million": 3.0,
        "output_price_per_million": 15.0,
        "cache_creation_price_per_million": 3.75,
        "cache_read_price_per_million": 0.30,
    },
    {
        "model": "claude-haiku-4-5",
        "input_price_per_million": 0.80,
        "output_price_per_million": 4.0,
        "cache_creation_price_per_million": 1.0,
        "cache_read_price_per_million": 0.08,
    },
]

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
        # Seed default pricing — INSERT OR IGNORE so existing rows are never overwritten
        now = datetime.now(timezone.utc).isoformat()
        for p in _DEFAULT_PRICING:
            conn.execute(
                """
                INSERT OR IGNORE INTO model_pricing
                    (model, input_price_per_million, output_price_per_million,
                     cache_creation_price_per_million, cache_read_price_per_million,
                     currency, updated_at)
                VALUES (?, ?, ?, ?, ?, 'USD', ?)
                """,
                (
                    p["model"],
                    p["input_price_per_million"],
                    p["output_price_per_million"],
                    p["cache_creation_price_per_million"],
                    p["cache_read_price_per_million"],
                    now,
                ),
            )
        conn.commit()
