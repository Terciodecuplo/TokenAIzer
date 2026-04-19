# client-configuration Specification

## Purpose
Automatically manage the configuration of local clients (Claude Code,
custom agents) so they route API traffic through the TokenAIzer proxy
without requiring manual setup. Configuration changes are triggered by
proxy lifecycle events.

## Requirements

### Requirement: Automatic base URL injection [FUTURE]
The system SHALL automatically write `ANTHROPIC_BASE_URL=http://localhost:8090`
to the project `.env` file when the proxy starts.

### Requirement: Automatic base URL removal [FUTURE]
The system SHALL remove the `ANTHROPIC_BASE_URL` entry from the project
`.env` file when the proxy stops, restoring the default Anthropic API
endpoint for all clients.

### Requirement: Non-destructive env file editing [FUTURE]
The system SHALL preserve all other entries in the `.env` file when
adding or removing `ANTHROPIC_BASE_URL`. It SHALL NOT overwrite or
delete unrelated variables.

### Requirement: Client source separation [FUTURE]
The system SHALL support tagging usage events by source, distinguishing
between Claude Code conversation traffic, Claude Code agent traffic,
and custom agent traffic via the `metadata` field in API requests.

### Requirement: Graceful fallback [FUTURE]
The system SHALL handle the case where the `.env` file does not exist
by creating it with only the `ANTHROPIC_BASE_URL` entry on proxy start,
and removing it entirely on proxy stop if it was created by the system.

#### Scenario: Proxy started with existing .env [FUTURE]
- GIVEN a `.env` file exists with other variables
- WHEN the proxy starts
- THEN `ANTHROPIC_BASE_URL=http://localhost:8090` is appended
- AND all existing variables are preserved

#### Scenario: Proxy stopped [FUTURE]
- GIVEN the proxy is running and `.env` contains `ANTHROPIC_BASE_URL`
- WHEN the proxy stops
- THEN `ANTHROPIC_BASE_URL` is removed from `.env`
- AND all other variables remain untouched

#### Scenario: Proxy stopped with no .env [FUTURE]
- GIVEN no `.env` file exists
- WHEN the proxy stops
- THEN no file is created or modified
- AND no error is raised