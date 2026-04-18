## 1. Project Scaffold

- [x] 1.1 Create `dashboard/package.json` with `svelte`, `vite`, and `@sveltejs/vite-plugin-svelte` as dev dependencies and `chart.js` as a dependency
- [x] 1.2 Create `dashboard/vite.config.js` with the Svelte plugin and a proxy rule forwarding `/api` requests to `http://localhost:8000`
- [x] 1.3 Create `dashboard/index.html` entry point mounting the Svelte app
- [x] 1.4 Create `dashboard/src/main.js` bootstrapping `App.svelte`

## 2. API Layer

- [x] 2.1 Create `dashboard/src/api.js` with functions: `fetchSummary()`, `fetchHistory(limit)`, `fetchProxyStatus()`, `startProxy()`, `stopProxy()`
- [x] 2.2 Create `dashboard/src/exchangeRate.js` that fetches the USD→EUR rate from `api.frankfurter.app` and exports a writable store; defaults to `null` on failure

## 3. Count-Up Animation Utility

- [x] 3.1 Create `dashboard/src/animate.js` with an `animateValue(from, to, duration, onUpdate)` function using `requestAnimationFrame` and an ease-out curve

## 4. App Layout & State

- [x] 4.1 Create `dashboard/src/App.svelte` with reactive state variables: `summary`, `history`, `proxyStatus`, `eurRate`, `loading`
- [x] 4.2 In `onMount`: fetch proxy status, summary, history, and EUR rate; populate reactive state
- [x] 4.3 Implement `toggleProxy()` function: call start/stop API, update `proxyStatus`, start/stop auto-refresh interval
- [x] 4.4 Implement the 10-second `setInterval` that re-fetches summary and history when proxy is `running`; clear on `onDestroy`

## 5. UI Sections

- [x] 5.1 Render the global totals section: display `total.input_tokens`, `total.output_tokens`, `total.thinking_tokens`, `total.cache_creation_tokens`, `total.cache_read_tokens`
- [x] 5.2 Render estimated cost in USD (`total.estimated_cost`); render EUR equivalent if `eurRate` is available, otherwise show warning note
- [x] 5.3 Render per-model cards from `summary.models`: model name, token totals, estimated cost
- [x] 5.4 Render the proxy power button with active/inactive visual state bound to `proxyStatus`
- [x] 5.5 Wire count-up animation: call `animateValue` for each numeric field whenever `summary` updates

## 6. Chart

- [x] 6.1 Add a `<canvas bind:this={chartCanvas}>` element in `App.svelte`
- [x] 6.2 In `onMount`, initialise a Chart.js `Line` chart on the canvas with two datasets: `input_tokens` and `output_tokens`, using `history` events as data points (x = timestamp, y = token count)
- [x] 6.3 Update the chart datasets and call `chart.update()` whenever `history` is refreshed
- [x] 6.4 Display an empty-state message overlay when `history` is empty
- [x] 6.5 Call `chart.destroy()` in `onDestroy` to prevent canvas reuse errors
- [x] 6.6 Apply Chart.js visual config from visual-design spec: transparent background, grid lines #1f1f1f, axis labels #555555 11px, line width 1.5px, point radius 0, gradient fill from series color at 0.15 opacity to transparent, custom tooltip matching spec

## 7. Styling

- [x] 7.1 Create `dashboard/src/app.css` implementing the full visual-design spec:
  - CSS custom properties for the complete color system (#0a0a0a base, #5e6ad2 accent)
  - Geist font loaded from https://vercel.com/font with Inter as fallback
  - Metric value typography: 48px weight-600 tabular-nums letter-spacing -0.03em
  - Metric label typography: 11px uppercase weight-500 letter-spacing 0.08em text-secondary
  - Card style: background #111111, border 0.5px solid #1f1f1f, border-radius 8px, padding 20px 24px, no box-shadow
  - Power button: 56px circle, idle (#1a1a1a border #2a2a2a), active (#1e2040 border #5e6ad2 glow rgba(94,106,210,0.15))
  - Status indicator: 8px circle, active (#4caf7d with pulse animation), idle (#555555)
  - Chart.js colors: input #5e6ad2, output #4caf7d, thinking #e5a03a, cache #888888
  - Chart tooltip: background #1a1a1a, border #2a2a2a, border-radius 6px
  - Page load stagger: cards translateY(8px)→0 + opacity 0→1, 300ms, 50ms delay between cards
  - Settings panel: gear icon top-right, absolute dropdown background #1a1a1a border #2a2a2a, fade + translateY animation 150ms
- [x] 7.2 Import `app.css` in `main.js`
- [x] 7.3 Add graph interval selector to settings panel: options "By hour" (default) and "By day", stored in a Svelte writable store, passed to `fetchHistory()` as a query parameter
