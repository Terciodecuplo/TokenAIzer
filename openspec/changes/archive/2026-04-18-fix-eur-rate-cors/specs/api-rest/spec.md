## ADDED Requirements

### Requirement: GET /api/exchange-rate endpoint
The REST API SHALL include a `GET /api/exchange-rate` endpoint that returns the current USD→EUR exchange rate proxied from Frankfurter. The response body SHALL conform to `{ "eur": number | null }`.

#### Scenario: Endpoint is reachable
- **WHEN** a client sends `GET /api/exchange-rate`
- **THEN** the server returns HTTP 200 with a JSON body containing the key `"eur"`
