## Context

All seven REST endpoints exist and are wired in `backend/main.py`. The only behavioural gap is in `GET /api/usage/summary`: when the `usage_events` table is empty the query returns no rows, so the `models` array in the response is `[]`. The spec requires all supported models to appear with zero values so the dashboard can render an empty-state chart immediately without special-casing a missing model list.

The fix is a LEFT JOIN between the `model_pricing` table (which is always seeded with three rows) and the aggregated `usage_events` query, so every pricing row appears in the result regardless of whether it has any events.

## Goals / Non-Goals

**Goals:**
- Fix `get_usage_summary()` to return all seeded models with zero counts when no events exist
- Add a comprehensive `TestClient`-based test suite for every API endpoint

**Non-Goals:**
- Pagination metadata in history response (future change)
- Authentication or rate limiting
- OpenAPI schema validation tests

## Decisions

### 1. LEFT JOIN on model_pricing in get_usage_summary

**Decision**: Replace the `GROUP BY model` query on `usage_events` with a `LEFT JOIN` from `model_pricing` to `usage_events`, using `COALESCE` to default aggregated values to `0`.

```sql
SELECT p.model,
       COALESCE(SUM(e.input_tokens), 0)          AS input_tokens,
       ...
FROM model_pricing p
LEFT JOIN usage_events e ON e.model = p.model
GROUP BY p.model
```

**Rationale**: A single query, no application-level padding, and the result automatically tracks whatever models are in the pricing table. If a new model is added to the seed, it appears in the summary with zeros at no extra cost.

**Alternative considered**: Padding in Python after the query — add a loop that inserts zero-value entries for any seeded model not in the result set. Works, but requires two queries and model-list awareness in the application layer.

---

### 2. TestClient with monkeypatched DB_PATH for API tests

**Decision**: Reuse the same `monkeypatch` + temp-file pattern from `test_persistence.py`. Import `main.app` after patching `db.database.DB_PATH` so the FastAPI app and all its dependencies write to an isolated temp file.

**Rationale**: Consistent with the existing test strategy; no extra fixtures or test databases to manage.

## Risks / Trade-offs

- **LEFT JOIN couples summary to pricing table** → If a model is used via the proxy but not in `model_pricing`, its events won't appear in the summary. Acceptable: all supported models are seeded, and any future model should be seeded too.
- **Test isolation via temp file** → Slightly slower than in-memory SQLite but avoids the connection-sharing issues of `:memory:` across the FastAPI dependency graph.
