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
            SELECT p.model,
                   p.input_price_per_million,
                   p.output_price_per_million,
                   p.cache_creation_price_per_million,
                   p.cache_read_price_per_million,
                   COALESCE(SUM(e.input_tokens), 0)          AS input_tokens,
                   COALESCE(SUM(e.output_tokens), 0)         AS output_tokens,
                   COALESCE(SUM(e.thinking_tokens), 0)       AS thinking_tokens,
                   COALESCE(SUM(e.cache_creation_tokens), 0) AS cache_creation_tokens,
                   COALESCE(SUM(e.cache_read_tokens), 0)     AS cache_read_tokens
            FROM model_pricing p
            LEFT JOIN usage_events e ON e.model = p.model
            GROUP BY p.model
            ORDER BY p.model
            """
        ).fetchall()

    models = []
    totals = {k: 0 for k in ("input_tokens", "output_tokens", "thinking_tokens",
                              "cache_creation_tokens", "cache_read_tokens")}
    totals["estimated_cost"] = 0.0

    for row in rows:
        cost = (
            row["input_tokens"]            * (row["input_price_per_million"] / 1_000_000)
            + row["output_tokens"]         * (row["output_price_per_million"] / 1_000_000)
            + row["cache_creation_tokens"] * (row["cache_creation_price_per_million"] / 1_000_000)
            + row["cache_read_tokens"]     * (row["cache_read_price_per_million"] / 1_000_000)
        )
        entry = {
            "model":                  row["model"],
            "input_tokens":           row["input_tokens"],
            "output_tokens":          row["output_tokens"],
            "thinking_tokens":        row["thinking_tokens"],
            "cache_creation_tokens":  row["cache_creation_tokens"],
            "cache_read_tokens":      row["cache_read_tokens"],
            "estimated_cost":         round(cost, 6),
        }
        models.append(entry)
        for k in ("input_tokens", "output_tokens", "thinking_tokens",
                  "cache_creation_tokens", "cache_read_tokens"):
            totals[k] += row[k]
        totals["estimated_cost"] += cost

    totals["estimated_cost"] = round(totals["estimated_cost"], 6)
    return {"models": models, "total": totals}


def get_usage_breakdown(
    model: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    conditions = ["e.model = ?"]
    params: list = [model]
    if date_from:
        conditions.append("e.timestamp >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("e.timestamp <= ?")
        params.append(date_to)

    where = " AND ".join(conditions)

    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT p.input_price_per_million,
                   p.output_price_per_million,
                   p.cache_creation_price_per_million,
                   p.cache_read_price_per_million,
                   COALESCE(SUM(e.input_tokens), 0)          AS input_tokens,
                   COALESCE(SUM(e.output_tokens), 0)         AS output_tokens,
                   COALESCE(SUM(e.thinking_tokens), 0)       AS thinking_tokens,
                   COALESCE(SUM(e.cache_creation_tokens), 0) AS cache_creation_tokens,
                   COALESCE(SUM(e.cache_read_tokens), 0)     AS cache_read_tokens
            FROM model_pricing p
            LEFT JOIN usage_events e ON e.model = p.model AND {where}
            WHERE p.model = ?
            GROUP BY p.model
            """,
            params + [model],
        ).fetchone()

    zero = {
        "model": model, "period": None,
        "input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0,
        "cache_creation_tokens": 0, "cache_read_tokens": 0,
        "input_cost": 0.0, "output_cost": 0.0, "thinking_cost": 0.0,
        "cache_creation_cost": 0.0, "cache_read_cost": 0.0, "total_cost": 0.0,
    }
    if not row:
        return zero

    ipm  = row["input_price_per_million"] / 1_000_000
    opm  = row["output_price_per_million"] / 1_000_000
    ccpm = row["cache_creation_price_per_million"] / 1_000_000
    crpm = row["cache_read_price_per_million"] / 1_000_000

    input_cost   = row["input_tokens"]            * ipm
    output_cost  = row["output_tokens"]           * opm
    think_cost   = row["thinking_tokens"]         * opm   # thinking billed at output rate
    cc_cost      = row["cache_creation_tokens"]   * ccpm
    cr_cost      = row["cache_read_tokens"]       * crpm
    total_cost   = input_cost + output_cost + think_cost + cc_cost + cr_cost

    return {
        "model":                  model,
        "period":                 None,
        "input_tokens":           row["input_tokens"],
        "output_tokens":          row["output_tokens"],
        "thinking_tokens":        row["thinking_tokens"],
        "cache_creation_tokens":  row["cache_creation_tokens"],
        "cache_read_tokens":      row["cache_read_tokens"],
        "input_cost":             round(input_cost, 6),
        "output_cost":            round(output_cost, 6),
        "thinking_cost":          round(think_cost, 6),
        "cache_creation_cost":    round(cc_cost, 6),
        "cache_read_cost":        round(cr_cost, 6),
        "total_cost":             round(total_cost, 6),
    }


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
