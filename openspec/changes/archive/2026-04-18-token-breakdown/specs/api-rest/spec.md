## ADDED Requirements

### Requirement: Usage breakdown endpoint
The system SHALL expose `GET /api/usage/breakdown` accepting query parameters `model` (required) and `period` (one of `today`, `7d`, `30d`, `all`; default `all`). The response SHALL return a JSON object with keys `model`, `period`, `input_tokens`, `output_tokens`, `thinking_tokens`, `cache_creation_tokens`, `cache_read_tokens`, `input_cost`, `output_cost`, `thinking_cost`, `cache_creation_cost`, `cache_read_cost`, and `total_cost`. All token counts and costs SHALL default to `0` when no events exist.

#### Scenario: Breakdown for model with data
- **WHEN** `GET /api/usage/breakdown?model=claude-sonnet-4-6&period=7d` is called and events exist within the last 7 days
- **THEN** the response is HTTP 200 with aggregated token counts and costs for that model in that period

#### Scenario: Breakdown for model with no data in period
- **WHEN** `GET /api/usage/breakdown?model=claude-sonnet-4-6&period=today` is called and no events exist today
- **THEN** the response is HTTP 200 with all token counts and costs set to `0`

#### Scenario: Unknown model
- **WHEN** `GET /api/usage/breakdown?model=unknown-model` is called
- **THEN** the response is HTTP 200 with all token counts and costs set to `0`
