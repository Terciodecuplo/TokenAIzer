from datetime import datetime, timezone

from .database import get_connection


def upsert_pricing(model: str, prices: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO model_pricing
                (model, input_price_per_million, output_price_per_million,
                 cache_creation_price_per_million, cache_read_price_per_million,
                 currency, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                model,
                prices.get("input_price_per_million", 0),
                prices.get("output_price_per_million", 0),
                prices.get("cache_creation_price_per_million", 0),
                prices.get("cache_read_price_per_million", 0),
                prices.get("currency", "USD"),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def get_all_pricing() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM model_pricing ORDER BY model").fetchall()
    return [dict(r) for r in rows]
