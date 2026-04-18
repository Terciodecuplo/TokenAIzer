# exchange-rate Specification

## Purpose
Provide a backend proxy for fetching the USD→EUR exchange rate from Frankfurter, avoiding direct browser-to-Frankfurter requests that may be blocked by CORS.

## Requirements

### Requirement: Backend proxy for USD→EUR exchange rate
The system SHALL expose `GET /api/exchange-rate` which fetches the current USD→EUR rate from `https://api.frankfurter.app/latest?from=USD&to=EUR` server-side and returns it as JSON. The endpoint SHALL always return HTTP 200. On success it returns `{ "eur": <float> }`; on any fetch or parse failure it returns `{ "eur": null }`.

#### Scenario: Successful rate fetch
- **WHEN** Frankfurter responds with a valid JSON body containing `rates.EUR`
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": <float> }` where the value matches `rates.EUR`

#### Scenario: Frankfurter unreachable
- **WHEN** the upstream request to Frankfurter raises an exception (timeout, DNS failure, etc.)
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": null }`

#### Scenario: Frankfurter returns unexpected JSON
- **WHEN** the upstream response body does not contain `rates.EUR`
- **THEN** the endpoint returns HTTP 200 with body `{ "eur": null }`
