## MODIFIED Requirements

### Requirement: EUR exchange rate display
The dashboard SHALL fetch the USD→EUR exchange rate from `/api/exchange-rate` (the backend proxy) instead of calling `https://api.frankfurter.app` directly. All other behavior (showing EUR equivalent when rate is available, showing "EUR rate unavailable" when `null`) remains unchanged.

#### Scenario: Rate available via backend proxy
- **WHEN** `GET /api/exchange-rate` returns `{ "eur": <float> }`
- **THEN** the dashboard displays the EUR equivalent of the estimated cost

#### Scenario: Rate unavailable
- **WHEN** `GET /api/exchange-rate` returns `{ "eur": null }`
- **THEN** the dashboard shows "EUR rate unavailable" in place of the EUR cost
