## Why

The Frankfurter API (`api.frankfurter.app`) does not send CORS headers that permit browser-originated requests from `localhost:5173`, causing the EUR exchange rate fetch to fail silently in the dashboard. Moving the fetch to the backend eliminates the browser CORS constraint entirely.

## What Changes

- New FastAPI endpoint `GET /api/exchange-rate` that fetches `https://api.frankfurter.app/latest?from=USD&to=EUR` server-side and returns `{ "eur": <rate> }` as JSON
- `dashboard/src/exchangeRate.js` updated to call `/api/exchange-rate` instead of the Frankfurter URL directly
- Backend `httpx` (or `urllib`) used for the server-side HTTP call; no new runtime dependency if `httpx` is already available via FastAPI's optional extras, otherwise use `urllib.request`

## Capabilities

### New Capabilities

- `exchange-rate`: Backend proxy endpoint that fetches and returns the current USD→EUR exchange rate

### Modified Capabilities

- `api-rest`: Adds `GET /api/exchange-rate` to the REST surface
- `dashboard-overview`: `exchangeRate.js` fetch target changes from external Frankfurter URL to `/api/exchange-rate`

## Impact

- **Backend**: new route file `backend/api/exchange_rate.py`, registered in `backend/main.py`
- **Frontend**: `dashboard/src/exchangeRate.js` — one-line URL change
- **Tests**: one new test in `backend/tests/test_api_routes.py` covering the happy path and the failure/fallback case
- **Dependencies**: `httpx` is already present as a test dependency; used at runtime here too (or `urllib.request` as zero-dep alternative)
