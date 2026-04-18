## MODIFIED Requirements

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
