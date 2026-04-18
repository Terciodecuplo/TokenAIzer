## 1. Backend — Breakdown Query

- [x] 1.1 Add `get_usage_breakdown(model, date_from, date_to)` to `backend/db/usage.py`: LEFT JOIN `model_pricing` onto `usage_events` filtered by model + date range; return token counts and per-category costs (count × price_per_million / 1_000_000); default all values to `0`
- [x] 1.2 Add `_period_to_dates(period)` helper in `backend/api/breakdown.py` that maps `today` / `7d` / `30d` / `all` to `(date_from, date_to)` UTC datetime strings (or `None` for `all`)

## 2. Backend — Breakdown Endpoint

- [x] 2.1 Create `backend/api/breakdown.py` with a FastAPI router exposing `GET /api/usage/breakdown?model=&period=`; call `get_usage_breakdown`; return the full response schema
- [x] 2.2 Register the breakdown router in `backend/main.py`

## 3. Backend — Tests

- [x] 3.1 Add tests to `backend/tests/test_api_routes.py`: breakdown with data returns correct aggregated counts; breakdown with no data returns all zeros; period=today excludes old events

## 4. Frontend — API helper

- [x] 4.1 Add `fetchBreakdown(model, period)` to `dashboard/src/api.js` that calls `GET /api/usage/breakdown?model=<model>&period=<period>`

## 5. Frontend — Breakdown Section in App.svelte

- [x] 5.1 Add reactive state: `breakdownModel` (default to first model in `summary.models`), `breakdownPeriod` (default `'all'`), `breakdown` (response object)
- [x] 5.2 Add `loadBreakdown()` async function that calls `fetchBreakdown(breakdownModel, breakdownPeriod)` and sets `breakdown`
- [x] 5.3 Call `loadBreakdown()` in `onMount` and whenever `breakdownModel` or `breakdownPeriod` changes (reactive `$:` block)
- [x] 5.4 Include `loadBreakdown()` in the 10-second auto-refresh cycle
- [x] 5.5 Render the breakdown section: model `<select>` populated from `summary.models`, four period filter buttons, per-category rows (label / token count / cost / percentage bar), thinking row conditional on `breakdown.thinking_tokens > 0`

## 6. Styling

- [x] 6.1 Add CSS for breakdown table rows, percentage bar track and fill, period button selected state, and model select input to `dashboard/src/app.css`
