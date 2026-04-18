## 1. Fix Usage Summary Zero-Data Behaviour

- [x] 1.1 Rewrite the SQL in `get_usage_summary()` in `backend/db/usage.py` to use a LEFT JOIN from `model_pricing` onto `usage_events`, with `COALESCE` defaulting all token sums to `0`
- [x] 1.2 Verify the Python aggregation loop handles rows where all token values are `0` without raising errors

## 2. API Tests

- [x] 2.1 Create `backend/tests/test_api_routes.py` with a `client` fixture that patches `db.database.DB_PATH` to a temp file, calls `init_db()`, and returns a `TestClient(app)`
- [x] 2.2 Test `GET /api/usage/summary` returns all seeded models with zero counts when no events exist
- [x] 2.3 Test `GET /api/usage/summary` returns correct per-model totals after inserting events
- [x] 2.4 Test `GET /api/usage/history` with no filters returns all events
- [x] 2.5 Test `GET /api/usage/history?source=proxy` excludes manual events
- [x] 2.6 Test `GET /api/usage/history?model=claude-sonnet-4-6` returns only matching events
- [x] 2.7 Test `POST /api/usage/manual` returns `201` and creates a retrievable event
- [x] 2.8 Test `POST /api/usage/manual` with missing `model` returns `400`
- [x] 2.9 Test `GET /api/pricing` returns all seeded models
- [x] 2.10 Test CORS header `Access-Control-Allow-Origin` is present on responses
