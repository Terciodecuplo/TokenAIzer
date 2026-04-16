## MODIFIED Requirements

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
