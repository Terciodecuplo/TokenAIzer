## Context

The dashboard currently exposes only global totals (via `/api/usage/summary`) and raw event history (via `/api/usage/history`). The `token-breakdown` spec requires a per-model, per-category aggregated view that can be filtered by time period. The backend must supply pre-aggregated figures; sending raw events to the frontend and aggregating in JS is wasteful and couples the UI to the event schema.

The summary endpoint does not support time-period filtering, so a new endpoint is needed.

## Goals / Non-Goals

**Goals:**
- New `GET /api/usage/breakdown?model=<model>&period=<today|7d|30d|all>` endpoint returning token counts, costs, and totals for one model in one period
- Frontend breakdown section: model selector, period filter, per-category rows (count + cost + percentage bar), conditional thinking row
- Thinking row hidden when `thinking_tokens == 0`

**Non-Goals:**
- Cross-model comparison in a single view
- Export / download of breakdown data
- Custom date range picker (only the four preset periods)
- Pagination of the breakdown data

## Decisions

### 1. New `GET /api/usage/breakdown` endpoint rather than client-side aggregation

**Decision**: Add a dedicated endpoint that accepts `model` and `period` query params and returns pre-aggregated totals.

**Rationale**: The history endpoint already returns up to 500 raw events. Sending all events to the browser and summing them in JS works but is O(n) in JS, duplicates business logic (pricing multiplication), and exposes raw internal data. A server-side aggregation is simpler, reuses `model_pricing` join logic already in `get_usage_summary()`, and makes the frontend stateless.

**Alternative considered**: Client-side aggregation from history — simpler to implement (no new endpoint) but ties the UI to raw event shape and requires the frontend to know pricing rates.

### 2. Period expressed as a named preset, not raw dates

**Decision**: The endpoint accepts `period` as one of `today`, `7d`, `30d`, `all`. The backend resolves to `date_from` / `date_to` internally.

**Rationale**: The frontend only needs to pass a string token; date math lives in one place (the backend). If a custom range is needed in the future, `date_from` / `date_to` params can be added without changing the UI contract.

### 3. Breakdown section is a collapsible panel appended below the chart in `App.svelte`

**Decision**: Extend the single `App.svelte` with a new `<section class="section">` block. No new component file.

**Rationale**: Consistent with the existing design decision (single-component app); four UI elements (selector, buttons, table, bars) don't justify a new file at this scale.

### 4. Percentage bars implemented as plain `<div>` with inline `width` style

**Decision**: CSS `width: <N>%` on a coloured inner div inside a fixed-height track div.

**Rationale**: No library needed; fully controllable; matches the visual spec's minimal aesthetic. Animating width change via CSS `transition` is one line.

## Risks / Trade-offs

- **`today` period boundary** → "Today" is defined as UTC midnight to now on the backend. If the user's local timezone differs, early-morning events may appear in the wrong bucket. Acceptable for a local dev tool; a timezone param can be added later.
- **Model with zero events for the period** → The endpoint returns all categories as `0` (same defensive pattern as the summary endpoint). The UI shows all zeros with no percentage bars.
- **Thinking tokens visibility** → Determined by `thinking_tokens == 0` on the response; the frontend hides the row. A model with exactly zero thinking tokens (but that theoretically supports thinking) would hide the row — this matches the spec's stated condition.
