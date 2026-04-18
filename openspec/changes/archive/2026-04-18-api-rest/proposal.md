## Why

The REST API routes were scaffolded in earlier changes but lack two things: a correct zero-data response from `GET /api/usage/summary` (the spec says it must return all known models with zero values, but the current implementation returns an empty list) and a test suite that verifies every endpoint contract. Adding these closes the gap between what is specified and what is deployed.

## What Changes

- Fix `get_usage_summary()` in `backend/db/usage.py` to always include all seeded models even when they have zero usage events
- Add `source` query parameter documentation to `GET /api/usage/history` (already implemented, needs spec alignment verification)
- Add `backend/tests/test_api_routes.py` covering every REST endpoint with a `TestClient` and an isolated in-memory database
- Verify CORS headers are present on all responses

## Capabilities

### New Capabilities

(none — completing the existing `api-rest` spec)

### Modified Capabilities

- `api-rest`: Requirement "Usage summary endpoint" gains a scenario specifying the zero-data behaviour (return all seeded models with zero values, not an empty list). Requirement "Usage history endpoint" gains explicit `source` query parameter documentation.

## Impact

- **`backend/db/usage.py`**: `get_usage_summary()` joins with `model_pricing` to include all known models in the response even with no events
- **`backend/tests/test_api_routes.py`**: new test module
- No schema or table changes required
