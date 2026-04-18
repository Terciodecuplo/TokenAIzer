## Context

The backend exposes seven REST endpoints (summary, history, pricing, proxy lifecycle, manual entry) at `localhost:8000`. The dashboard is a standalone Svelte SPA served by Vite at `localhost:5173`. It communicates with the backend via `fetch()` — CORS is already configured to allow any localhost origin.

The spec requires:
- Global totals + per-model cards (from `GET /api/usage/summary`)
- USD and EUR cost (EUR requires a live exchange rate)
- Proxy power button (from `POST /api/proxy/start|stop` + `GET /api/proxy/status`)
- Auto-refresh every 10 seconds while proxy is active
- Count-up animation on numeric changes
- Time-series chart (from `GET /api/usage/history`)

## Goals / Non-Goals

**Goals:**
- Scaffold `dashboard/` as a Vite + Svelte project
- Single-page app (`App.svelte`) with all required sections
- Chart.js for the time-series visualisation
- USD → EUR conversion via `api.frankfurter.app` (free, no key required)
- Count-up animation using a simple interpolation utility
- Auto-refresh via `setInterval` scoped to proxy-active state

**Non-Goals:**
- Routing / multiple pages
- Authentication
- Dark mode
- Mobile layout optimisation
- Persisting the exchange rate (fetched once on load, cached in memory)

## Decisions

### 1. Single `App.svelte` component

**Decision**: Implement the entire dashboard in `App.svelte` with reactive `$:` blocks and Svelte stores for shared state. No component library.

**Rationale**: The dashboard has one page and four discrete sections. Splitting into sub-components adds boilerplate without reducing complexity at this scale. A single file keeps the implementation reviewable in one pass.

**Alternative considered**: Component per section (`GlobalTotals.svelte`, `ModelCards.svelte`, etc.) — cleaner separation but overkill for v1.

---

### 2. Chart.js via CDN or npm

**Decision**: Install `chart.js` via npm and import it directly in the Svelte component.

**Rationale**: Vite bundles it cleanly; no CDN dependency at runtime. The `<canvas>` element is bound via `bind:this` and the chart instance is created in `onMount`.

---

### 3. EUR exchange rate from `api.frankfurter.app`

**Decision**: Fetch `https://api.frankfurter.app/latest?from=USD&to=EUR` once on dashboard load. Cache the rate in a Svelte writable store. If the fetch fails, display USD only with a small warning.

**Rationale**: Frankfurter is free, open, requires no API key, and returns a simple JSON object. The daily rate is sufficient for cost estimation purposes.

---

### 4. Count-up animation via `requestAnimationFrame`

**Decision**: Implement a lightweight `animateValue(from, to, duration, callback)` utility that uses `requestAnimationFrame` and an easing function. Called whenever a displayed number changes.

**Rationale**: Avoids a dependency (e.g., `countup.js`) for a straightforward feature. The utility is ~20 lines and fully controllable.

---

### 5. Auto-refresh via `setInterval` / `clearInterval`

**Decision**: Start a 10-second interval when proxy status becomes `running`; clear it when status becomes `stopped`. The interval fetches `GET /api/usage/summary` and `GET /api/usage/history` and updates reactive state.

**Rationale**: Simple and reliable. Svelte's reactivity handles the UI update automatically once the state is mutated.

## Risks / Trade-offs

- **CORS on history endpoint** → Already configured; no action needed.
- **Frankfurter rate limit** → Free tier; a single request per page load is well within limits.
- **Chart memory leak** → The Chart.js instance must be destroyed in Svelte's `onDestroy` to avoid canvas reuse errors on hot reload.
- **Large history datasets** → History is fetched with `limit=200` to keep the chart readable; older data is not shown.
