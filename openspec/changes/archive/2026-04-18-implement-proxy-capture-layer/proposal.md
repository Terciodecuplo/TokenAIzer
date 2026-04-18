## Why

TokenAIzer needs a mechanism to intercept real Anthropic API traffic without requiring changes to the client application. A local HTTP proxy is the lowest-friction path: it sits between any existing client and `api.anthropic.com`, extracts token usage from every response, and feeds the data to the persistence layer—giving the dashboard real-time cost visibility with zero SDK changes.

## What Changes

- Introduce a local HTTP proxy server that forwards requests to `api.anthropic.com` transparently
- Extract `usage` objects (input, output, cache creation/read, thinking tokens) from both non-streaming and SSE streaming responses
- Persist one usage event per API response via the data-persistence layer
- Expose a lifecycle API (`POST /proxy/start`, `POST /proxy/stop`, `GET /proxy/status`) consumed by the dashboard power button
- Default proxy port: `localhost:8080`

## Capabilities

### New Capabilities

- `proxy-capture`: Transparent HTTP proxy that intercepts Anthropic API traffic, extracts token usage from each response (including SSE streams), and persists usage events

### Modified Capabilities

- `api-rest`: Add lifecycle endpoints (`/proxy/start`, `/proxy/stop`, `/proxy/status`) to the existing REST surface

## Impact

- **New component**: proxy process (Node.js `http`/`http-proxy` or equivalent)
- **data-persistence**: proxy-capture writes usage events using the existing persistence interface
- **api-rest**: three new endpoints wired to proxy lifecycle
- **dashboard-overview**: power button activates/deactivates proxy via the new lifecycle endpoints
- **Dependencies**: requires an HTTP proxy library capable of streaming SSE without buffering
