# api-rest Specification

## Purpose
Expose a REST API that serves token usage data and proxy lifecycle
controls to the dashboard. Acts as the single interface between
the frontend and the backend.

## Requirements

### Requirement: Usage summary endpoint
The system SHALL expose `GET /api/usage/summary` returning total `input_tokens`, `output_tokens`, `thinking_tokens`, `cache_creation_tokens`, `cache_read_tokens`, and `estimated_cost` per model and as a global total. The response SHALL include an entry for every model present in the pricing table, even if that model has no recorded usage events, defaulting all token counts and cost to `0`.

#### Scenario: Summary requested with data
- **WHEN** `GET /api/usage/summary` is called and usage events exist
- **THEN** the response contains a `models` array with per-model token totals
- **AND** each entry includes `estimated_cost` calculated from stored pricing data

#### Scenario: No usage data yet
- **WHEN** `GET /api/usage/summary` is called and no usage events exist
- **THEN** the response contains a `models` array with one entry per seeded model
- **AND** all token counts and `estimated_cost` are `0` for every model
- **AND** the response does not return an error

### Requirement: Usage history endpoint
The system SHALL expose `GET /api/usage/history` accepting optional query parameters: `model`, `date_from`, `date_to`, `source` (`proxy` | `manual`), `limit`, and `offset`. All parameters are optional and combinable.

#### Scenario: History filtered by source
- **WHEN** `GET /api/usage/history?source=proxy` is called
- **THEN** only events with `source = "proxy"` are returned

#### Scenario: History with no filters
- **WHEN** `GET /api/usage/history` is called with no query parameters
- **THEN** all events are returned up to the default `limit`

### Requirement: Pricing endpoint
The system SHALL expose GET /api/pricing returning current stored
pricing data for all tracked models.

### Requirement: Proxy control endpoints
The system SHALL expose `POST /api/proxy/start` and `POST /api/proxy/stop` to control the proxy lifecycle. Both endpoints SHALL delegate to the proxy-capture lifecycle interface and return the resulting proxy status in the response body.

#### Scenario: Start proxy successfully
- **WHEN** `POST /api/proxy/start` is called and the proxy is stopped
- **THEN** the response is `200 OK` with body `{ "status": "running", "port": 8080 }`

#### Scenario: Proxy already running on start
- **WHEN** `POST /api/proxy/start` is called and the proxy is already running
- **THEN** the response is `200 OK` with body `{ "status": "running", "port": 8080 }`
- **AND** no second proxy instance is started

#### Scenario: Stop proxy successfully
- **WHEN** `POST /api/proxy/stop` is called and the proxy is running
- **THEN** the response is `200 OK` with body `{ "status": "stopped" }`

### Requirement: Proxy status endpoint
The system SHALL expose `GET /api/proxy/status` returning the current proxy state (`running` | `stopped`) and the port it is listening on when running.

#### Scenario: Status when running
- **WHEN** `GET /api/proxy/status` is called and the proxy is active
- **THEN** the response is `200 OK` with body `{ "status": "running", "port": 8080 }`

#### Scenario: Status when stopped
- **WHEN** `GET /api/proxy/status` is called and the proxy is inactive
- **THEN** the response is `200 OK` with body `{ "status": "stopped", "port": null }`

### Requirement: Manual entry endpoint
The system SHALL expose POST /api/usage/manual accepting a usage event
payload for cases where automatic capture is not available.

### Requirement: CORS
The system SHALL allow requests from localhost on any port to support
local dashboard development.

### Requirement: GET /api/exchange-rate endpoint
The REST API SHALL include a `GET /api/exchange-rate` endpoint that returns the current USD→EUR exchange rate proxied from Frankfurter. The response body SHALL conform to `{ "eur": number | null }`.

#### Scenario: Endpoint is reachable
- **WHEN** a client sends `GET /api/exchange-rate`
- **THEN** the server returns HTTP 200 with a JSON body containing the key `"eur"`