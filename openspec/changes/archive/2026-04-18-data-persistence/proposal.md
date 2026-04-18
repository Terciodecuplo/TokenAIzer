## Why

The proxy-capture change created skeleton DB tables and basic write/read functions, but pricing data management (upsert, read) and source-based query filtering are still missing. Completing the persistence layer now unblocks the REST API's `/api/pricing` endpoint and the cost calculation in the usage summary.

## What Changes

- Add `backend/db/pricing.py` with functions to upsert and read model pricing data
- Seed default pricing for the three supported models (`claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-opus-4-6`) on first run
- Add `source` filter to `get_usage_history` (currently only filters by model and date range)
- Add comprehensive unit tests for all persistence functions (`database`, `usage`, `pricing`)

## Capabilities

### New Capabilities

(none — implementing the existing `data-persistence` spec)

### Modified Capabilities

- `data-persistence`: Requirement "Query support" now explicitly requires filtering by `source` (`proxy` | `manual`). Requirement "Pricing storage" gains scenarios covering upsert behaviour and seed data on first run.

## Impact

- **`backend/db/`**: new `pricing.py` module; minor update to `usage.py` (source filter)
- **`backend/db/database.py`**: `init_db()` seeds default pricing rows if the table is empty
- **`backend/api/pricing.py`**: already wired — starts returning real data once pricing module exists
- **`backend/tests/`**: new `test_persistence.py` covering all DB functions
- **No schema changes** — `model_pricing` and `usage_events` tables are already correct
