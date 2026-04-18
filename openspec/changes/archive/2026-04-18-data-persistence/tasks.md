## 1. Pricing Module

- [x] 1.1 Create `backend/db/pricing.py` with `upsert_pricing(model, prices: dict) -> None` function using `INSERT OR REPLACE`
- [x] 1.2 Add `get_all_pricing() -> list[dict]` function to `backend/db/pricing.py`

## 2. Default Pricing Seed

- [x] 2.1 Add `INSERT OR IGNORE` seed statements to `init_db()` in `backend/db/database.py` for `claude-sonnet-4-6`, `claude-haiku-4-5`, and `claude-opus-4-6` with current Anthropic list prices
- [x] 2.2 Verify seed is idempotent: re-running `init_db()` must not overwrite existing rows

## 3. Query Support — Source Filter

- [x] 3.1 Add `source: Optional[str] = None` parameter to `get_usage_history()` in `backend/db/usage.py`
- [x] 3.2 Append `AND source = ?` condition when `source` is provided
- [x] 3.3 Update `backend/api/usage.py` history endpoint to pass `source` query param through to `get_usage_history`

## 4. Pricing API Wiring

- [x] 4.1 Confirm `backend/api/pricing.py` imports from `db.pricing` (or `db.database`) and returns live rows — no code change needed if already wired; verify by inspection

## 5. Tests

- [x] 5.1 Create `backend/tests/test_persistence.py` with a `db` fixture that creates an in-memory SQLite DB via `init_db()`
- [x] 5.2 Test: `write_usage_event` inserts a row with all token fields defaulting to `0` for absent keys
- [x] 5.3 Test: `get_usage_history` with no filters returns all events
- [x] 5.4 Test: `get_usage_history` filtered by `source="proxy"` excludes manual events
- [x] 5.5 Test: `get_usage_history` filtered by `model` and date range returns correct subset
- [x] 5.6 Test: `get_usage_summary` returns per-model totals and a global total with `estimated_cost`
- [x] 5.7 Test: `upsert_pricing` updates an existing row without creating duplicates
- [x] 5.8 Test: default seed rows exist after `init_db()` with an empty database
- [x] 5.9 Test: `get_all_pricing` returns all seeded models
