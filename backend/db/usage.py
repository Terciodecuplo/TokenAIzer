from datetime import datetime, timezone
from typing import Optional

from .database import get_connection


def write_usage_event(model: str, usage: dict, source: str = "proxy") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO usage_events
                (timestamp, model, input_tokens, output_tokens, thinking_tokens,
                 cache_creation_tokens, cache_read_tokens, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                model,
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
                usage.get("thinking_tokens", 0),
                usage.get("cache_creation_tokens", 0),
                usage.get("cache_read_tokens", 0),
                source,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_usage_summary() -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT model,
                   SUM(input_tokens)            AS input_tokens,
                   SUM(output_tokens)           AS output_tokens,
                   SUM(thinking_tokens)         AS thinking_tokens,
                   SUM(cache_creation_tokens)   AS cache_creation_tokens,
                   SUM(cache_read_tokens)       AS cache_read_tokens
            FROM usage_events
            GROUP BY model
            """
        ).fetchall()
        pricing_rows = conn.execute("SELECT * FROM model_pricing").fetchall()

    pricing = {r["model"]: dict(r) for r in pricing_rows}
    models = []
    totals = {k: 0 for k in ("input_tokens", "output_tokens", "thinking_tokens",
                              "cache_creation_tokens", "cache_read_tokens")}
    totals["estimated_cost"] = 0.0

    for row in rows:
        p = pricing.get(row["model"], {})
        cost = (
            row["input_tokens"]          * (p.get("input_price_per_million", 0) / 1_000_000)
            + row["output_tokens"]       * (p.get("output_price_per_million", 0) / 1_000_000)
            + row["cache_creation_tokens"] * (p.get("cache_creation_price_per_million", 0) / 1_000_000)
            + row["cache_read_tokens"]   * (p.get("cache_read_price_per_million", 0) / 1_000_000)
        )
        entry = {**dict(row), "estimated_cost": round(cost, 6)}
        models.append(entry)
        for k in ("input_tokens", "output_tokens", "thinking_tokens",
                  "cache_creation_tokens", "cache_read_tokens"):
            totals[k] += row[k]
        totals["estimated_cost"] += cost

    totals["estimated_cost"] = round(totals["estimated_cost"], 6)
    return {"models": models, "total": totals}


def get_usage_history(
    model: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list:
    conditions, params = [], []
    if model:
        conditions.append("model = ?")
        params.append(model)
    if date_from:
        conditions.append("timestamp >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("timestamp <= ?")
        params.append(date_to)
    if source:
        conditions.append("source = ?")
        params.append(source)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM usage_events {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
    return [dict(r) for r in rows]
