# proxy-capture Specification

## Purpose
Intercept HTTP traffic between any local client and the Anthropic API,
extract token usage from each response, and forward the data to the
persistence layer. The proxy runs on demand, controlled by the user
from the dashboard.

## Requirements

### Requirement: Request forwarding
The system SHALL forward all incoming HTTP requests received on `localhost:8080` to `api.anthropic.com`, preserving all headers, the request body, and HTTP method without modification.

#### Scenario: Non-streaming request forwarded
- **WHEN** a client sends a POST request to `http://localhost:8080/v1/messages` with a non-streaming body
- **THEN** the proxy forwards the request to `https://api.anthropic.com/v1/messages`
- **AND** returns the upstream response body and status code to the client unmodified

### Requirement: Usage extraction
The system SHALL extract the `usage` object from every Anthropic API response, capturing `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, and thinking tokens where present.

#### Scenario: Usage object present in response
- **WHEN** the upstream API response contains a `usage` field
- **THEN** the proxy reads all token count fields from the object
- **AND** defaults absent optional fields (e.g. thinking tokens) to `0`

### Requirement: Model identification
The system SHALL identify the model used in each request by reading the `model` field from the JSON request body.

#### Scenario: Model field present in request body
- **WHEN** the client sends a request with `"model": "claude-opus-4-7"` in the body
- **THEN** the proxy captures `claude-opus-4-7` as the model for the resulting usage event

### Requirement: Event persistence
The system SHALL write one usage event to the persistence layer per API response, including `timestamp`, `model`, all extracted token fields, and `source = "proxy"`.

#### Scenario: Usage event written after successful response
- **WHEN** the proxy receives a complete response from the upstream API
- **THEN** one row is inserted into the `usage_events` table
- **AND** all token fields are populated (defaulting absent fields to `0`)
- **AND** `source` is set to `"proxy"`

### Requirement: Streaming support
The system SHALL support Server-Sent Events (SSE) streaming responses. It SHALL pipe chunks to the client immediately and accumulate token usage from the final stream chunk, persisting the usage event only after the stream ends.

#### Scenario: Streaming response forwarded in real time
- **WHEN** the upstream response is `content-type: text/event-stream`
- **THEN** each SSE chunk is forwarded to the client as it arrives without buffering

#### Scenario: Token usage persisted after stream ends
- **WHEN** the proxy receives the final SSE chunk containing the `usage` object
- **THEN** the proxy extracts token counts from that chunk
- **AND** persists a single usage event after the stream closes

#### Scenario: Stream ends without usage data
- **WHEN** the final SSE chunk does not contain a parseable `usage` object
- **THEN** the proxy logs a warning
- **AND** does not persist a usage event for that request

### Requirement: On-demand lifecycle
The system SHALL expose a programmatic lifecycle interface allowing the backend to start and stop the proxy process on demand. The proxy SHALL default to stopped on backend startup.

#### Scenario: Proxy started
- **WHEN** the `start()` lifecycle function is called and the proxy is not already running
- **THEN** the proxy begins listening on `localhost:8080`
- **AND** returns a `running` status

#### Scenario: Proxy already running
- **WHEN** the `start()` lifecycle function is called and the proxy is already listening
- **THEN** no second instance is started
- **AND** a `running` status is returned

#### Scenario: Proxy stopped
- **WHEN** the `stop()` lifecycle function is called
- **THEN** the proxy stops accepting new connections
- **AND** returns a `stopped` status