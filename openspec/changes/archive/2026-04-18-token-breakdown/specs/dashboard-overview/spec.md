## ADDED Requirements

### Requirement: Token breakdown section
The dashboard SHALL include a "Token breakdown" section below the chart. The section SHALL contain a model selector, period filter buttons (Today / Last 7 days / Last 30 days / All time), and a per-category breakdown table fetched from `GET /api/usage/breakdown`.

#### Scenario: Dashboard loaded with no breakdown selection
- **WHEN** the dashboard loads
- **THEN** the breakdown section is visible with the first model pre-selected and period defaulting to "All time"
- **AND** the breakdown table shows values for that model and period

#### Scenario: Breakdown section reflects live data
- **WHEN** the auto-refresh cycle fires while the breakdown section is visible
- **THEN** the breakdown values update for the currently selected model and period
