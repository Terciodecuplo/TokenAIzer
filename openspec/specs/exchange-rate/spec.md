# exchange-rate Specification

## Purpose
Provide a backend proxy for fetching the USD→EUR exchange rate from open.er-api.com, avoiding direct browser requests that may be blocked by CORS.

## Requirements

### Requirement: Backend proxy for USD→EUR exchange rate
The system SHALL expose `GET /api/exchange-rate` which fetches the current USD→EUR rate from `https://open.er-api.com/v6/latest/USD` server-side and returns it as JSON. The endpoint SHALL always return HTTP 200. On success it returns `{ "eur": <float> }`; on any fetch or parse failure it returns `{ "eur": null }`.

#### Scenario: Successful rate fetch
- **WHEN** open.er-api.com responds with a valid JSON body containing `rates.EUR`
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": <float> }` where the value matches `rates.EUR`

#### Scenario: Provider unreachable
- **WHEN** the upstream request to open.er-api.com raises an exception (timeout, DNS failure, etc.)
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": null }`

#### Scenario: Provider returns unexpected JSON
- **WHEN** the upstream response body does not contain `rates.EUR`
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": null }`
