## ADDED Requirements

### Requirement: Dashboard scaffold
The system SHALL provide a Svelte + Vite project in the `dashboard/` directory that can be started with `npm run dev` and serves the dashboard at `localhost:5173`.

#### Scenario: Dev server starts
- **WHEN** the user runs `npm run dev` in `dashboard/`
- **THEN** the dashboard is accessible at `http://localhost:5173`
- **AND** it connects to the backend at `http://localhost:8000`

### Requirement: Global totals display
The system SHALL display total tokens consumed across all models broken down into `input`, `output`, `thinking`, `cache_creation`, and `cache_read` categories. Totals SHALL be sourced from `GET /api/usage/summary`.

#### Scenario: Totals shown on load
- **WHEN** the dashboard loads
- **THEN** global token totals are fetched and displayed
- **AND** zero values are shown if no events exist

### Requirement: Estimated cost display
The system SHALL display the estimated cost in USD. The system SHALL also display the estimated cost in EUR, converted using a daily exchange rate fetched from `api.frankfurter.app`. If the exchange rate fetch fails, the EUR value SHALL be omitted and a warning displayed.

#### Scenario: EUR conversion succeeds
- **WHEN** the dashboard loads and `api.frankfurter.app` is reachable
- **THEN** the estimated cost is shown in both USD and EUR

#### Scenario: EUR conversion fails
- **WHEN** the exchange rate fetch fails
- **THEN** only the USD cost is displayed
- **AND** a small warning note is shown

### Requirement: Per-model summary
The system SHALL display one card per model returned by `GET /api/usage/summary`, showing the model name, individual token totals, and estimated cost in USD.

#### Scenario: Model cards rendered
- **WHEN** the summary response includes entries for known models
- **THEN** one card is rendered per model
- **AND** each card shows token totals and estimated cost

### Requirement: Proxy power control
The system SHALL display a power button that calls `POST /api/proxy/start` or `POST /api/proxy/stop` depending on current state. The button SHALL reflect the proxy status (`active` | `inactive`) with a visible indicator.

#### Scenario: Proxy activated
- **WHEN** the user clicks the power button and the proxy is stopped
- **THEN** `POST /api/proxy/start` is called
- **AND** the button transitions to active state
- **AND** auto-refresh begins

#### Scenario: Proxy deactivated
- **WHEN** the user clicks the power button and the proxy is running
- **THEN** `POST /api/proxy/stop` is called
- **AND** the button transitions to inactive state
- **AND** auto-refresh stops

### Requirement: Auto-refresh
The system SHALL poll `GET /api/usage/summary` and `GET /api/usage/history` every 10 seconds while the proxy is active. Polling SHALL stop when the proxy is stopped or the page is unloaded.

#### Scenario: Auto-refresh active
- **WHEN** the proxy is running and 10 seconds elapse
- **THEN** summary and history data are re-fetched
- **AND** all displayed values update without a full page reload

### Requirement: Animated transitions
The system SHALL animate numeric value changes with a smooth count-up transition whenever displayed data updates.

#### Scenario: Data updates during active session
- **WHEN** a poll returns new totals
- **THEN** all changed numeric values animate from their previous value to the new value

### Requirement: Chart visualisation
The system SHALL display a Chart.js time-series chart showing token consumption over time, with separate lines for `input_tokens` and `output_tokens`. Data SHALL be sourced from `GET /api/usage/history?limit=200`. The chart SHALL display an empty-state message when no history exists.

#### Scenario: Chart renders with data
- **WHEN** history events exist
- **THEN** the chart shows a time-series line for input tokens and output tokens

#### Scenario: Chart empty state
- **WHEN** no history events exist
- **THEN** the chart area displays an empty-state message
