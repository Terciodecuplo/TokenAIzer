# dashboard-overview Specification

## Purpose
Provide a local web interface where the user can monitor global
token consumption across all models, control the proxy lifecycle,
and understand cost at a glance.

## Requirements

### Requirement: Global totals display
The system SHALL display total tokens consumed across all models,
broken down into input, output, thinking, and cache categories.

### Requirement: Estimated cost display
The system SHALL display the estimated cost in both USD and EUR,
converted using a daily exchange rate.

### Requirement: EUR exchange rate display
The dashboard SHALL fetch the USD→EUR exchange rate from `/api/exchange-rate` (the backend proxy) instead of calling open.er-api.com directly. All other behavior (showing EUR equivalent when rate is available, showing "EUR rate unavailable" when `null`) remains unchanged.

#### Scenario: Rate available via backend proxy
- **WHEN** `GET /api/exchange-rate` returns `{ "eur": <float> }`
- **THEN** the dashboard displays the EUR equivalent of the estimated cost

#### Scenario: Rate unavailable
- **WHEN** `GET /api/exchange-rate` returns `{ "eur": null }`
- **THEN** the dashboard shows "EUR rate unavailable" in place of the EUR cost

### Requirement: Per-model summary
The system SHALL display a card per model showing its individual
token totals and estimated cost.

### Requirement: Proxy power control
The system SHALL display a power button that starts and stops the
proxy, with a visible status indicator (active | inactive).

### Requirement: Auto-refresh
The system SHALL poll the API every 10 seconds when the proxy is
active and update all displayed values without a full page reload.

### Requirement: Animated transitions
The system SHALL animate numeric value changes with a smooth
count-up transition when data updates.

### Requirement: Chart visualisation
The system SHALL display a time-series chart showing token
consumption over time, with separate series for input and output.

#### Scenario: Proxy activated
- GIVEN the proxy is stopped
- WHEN the user clicks the power button
- THEN the button transitions to active state with animation
- AND the status indicator changes to active
- AND auto-refresh begins

#### Scenario: Data updates during active session
- GIVEN the proxy is running and the dashboard is open
- WHEN new usage events arrive and the poll returns new totals
- THEN all numeric values animate to their new values
- AND the chart updates with the new data point

#### Scenario: Dashboard opened with no data
- GIVEN no usage events exist yet
- WHEN the dashboard loads
- THEN all values display as zero
- AND the chart displays an empty state message
- AND the proxy button is visible and ready

### Requirement: Token breakdown section
The dashboard SHALL include a "Token breakdown" section below the chart. The section SHALL contain a model selector, period filter buttons (Today / Last 7 days / Last 30 days / All time), and a per-category breakdown table fetched from `GET /api/usage/breakdown`.

#### Scenario: Dashboard loaded with no breakdown selection
- **WHEN** the dashboard loads
- **THEN** the breakdown section is visible with the first model pre-selected and period defaulting to "All time"
- **AND** the breakdown table shows values for that model and period

#### Scenario: Breakdown section reflects live data
- **WHEN** the auto-refresh cycle fires while the breakdown section is visible
- **THEN** the breakdown values update for the currently selected model and period

### Requirement: Dashboard scaffold
The system SHALL provide a Svelte + Vite project in the `dashboard/` directory that can be started with `npm run dev` and serves the dashboard at `localhost:5173`.

#### Scenario: Dev server starts
- **WHEN** the user runs `npm run dev` in `dashboard/`
- **THEN** the dashboard is accessible at `http://localhost:5173`
- **AND** it connects to the backend at `http://localhost:8000`