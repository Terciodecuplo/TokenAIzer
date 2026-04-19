## Why

The backend API is fully implemented and tested. The project now needs its user-facing layer: a local Svelte dashboard that lets the user monitor token consumption, control the proxy, and understand cost at a glance. This is the primary output of TokenAIzer — without it, the backend has no consumer.

## What Changes

- Bootstrap the `dashboard/` Svelte + Vite project (package.json, vite.config, App.svelte)
- Implement the main dashboard layout with three sections: global totals, per-model cards, and a time-series chart
- Add a proxy power button wired to `POST /api/proxy/start` and `POST /api/proxy/stop`
- Implement auto-refresh: poll `GET /api/usage/summary` every 10 seconds while the proxy is running
- Implement count-up animation for all numeric values on data update
- Implement USD → EUR cost conversion using a daily exchange rate fetched from a free open exchange API
- Integrate Chart.js for the time-series chart (input tokens + output tokens over time, built from `GET /api/usage/history`)

## Capabilities

### New Capabilities

- `dashboard-overview`: The full Svelte dashboard application, from project scaffold to all interactive features

### Modified Capabilities

(none — all backend endpoints are already specified and implemented)

## Impact

- **New directory**: `dashboard/` (Svelte + Vite project)
- **Dependencies**: `svelte`, `vite`, `@sveltejs/vite-plugin-svelte`, `chart.js`
- **No backend changes** required — the dashboard consumes the existing REST API
- **Dev server**: `npm run dev` serves the dashboard at `localhost:5173`
