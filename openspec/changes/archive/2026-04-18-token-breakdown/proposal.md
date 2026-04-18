## Why

The dashboard currently shows only global totals and per-model cost cards. Users have no way to see how tokens are distributed across categories (input, output, thinking, cache) for a specific model, or how that distribution changes over time. The `token-breakdown` spec defines this view; this change implements it.

## What Changes

- New backend endpoint `GET /api/usage/breakdown` that aggregates token counts and costs per category for a given model and time period
- New "Breakdown" section added to `App.svelte` below the chart, featuring:
  - Model selector (dropdown of all models with recorded activity)
  - Period filter buttons: Today / Last 7 days / Last 30 days / All time
  - Per-category rows: token count, cost contribution, percentage horizontal bar
  - Thinking tokens row rendered only for models that support extended thinking
- New CSS rules for the breakdown table and bar components (added to `app.css`)

## Capabilities

### New Capabilities

- `token-breakdown`: Per-model, per-category token and cost breakdown with period filtering — **already specced** at `openspec/specs/token-breakdown/spec.md`; this change implements it

### Modified Capabilities

- `api-rest`: Adds `GET /api/usage/breakdown` endpoint to the REST surface
- `dashboard-overview`: Adds the breakdown section as a new panel within the single-page app

## Impact

- **Backend**: new route `backend/api/breakdown.py`, new DB query in `backend/db/usage.py`, registered in `backend/main.py`
- **Frontend**: new section in `dashboard/src/App.svelte`, new styles in `dashboard/src/app.css`
- **Tests**: new tests in `backend/tests/test_api_routes.py` for the breakdown endpoint; no new frontend tests
- **Dependencies**: none new
