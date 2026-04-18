## Context

TokenAIzer is a local desktop tool that tracks Anthropic API token consumption. Currently the persistence and REST layers are specified, but there is no mechanism to capture live traffic. Clients (SDKs, cURL, any HTTP tool) must be pointed at `localhost:8080` instead of `api.anthropic.com`. The proxy must be transparent—responses must arrive at the client unmodified and with full streaming support.

The backend is a local Python process (FastAPI + Uvicorn). The proxy runs as a managed subprocess spawned by the FastAPI backend, controlled via the existing `POST /api/proxy/start` and `POST /api/proxy/stop` REST endpoints already specified in `api-rest`.

## Goals / Non-Goals

**Goals:**
- Intercept HTTP(S) requests to `api.anthropic.com` on `localhost:8080`
- Extract `usage` from non-streaming JSON responses and SSE streaming responses
- Write one usage event per API call to the persistence layer
- Expose lifecycle controls (start/stop/status) wired to the REST layer
- Support all token fields: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, thinking tokens

**Non-Goals:**
- TLS/HTTPS interception (proxy targets HTTP; clients call `http://localhost:8080`)
- Multi-user or networked deployments (localhost only)
- Modifying or blocking requests
- Retry or error-correction logic on behalf of clients

## Decisions

### 1. Subprocess proxy over an in-process server

**Decision**: Implement the proxy as a Python subprocess spawned by the FastAPI backend using `mitmproxy` in inline script mode.

**Rationale**: `mitmproxy` provides native SSE support, transparent forwarding, and a clean scripting API for intercepting responses. Running it as a subprocess keeps the proxy lifecycle independent from the FastAPI process, so a proxy crash does not bring down the REST API.

**Alternative considered**: Custom proxy using `http.server` + `httpx` — avoids the `mitmproxy` dependency but requires manually implementing SSE passthrough and chunk accumulation, adding complexity for no benefit.

---

### 2. SSE streaming: pipe-then-intercept pattern

**Decision**: For streaming responses (`content-type: text/event-stream`), pipe the upstream response directly to the client socket while simultaneously parsing chunks through an SSE accumulator. Persist usage only after the `[DONE]` sentinel is received.

**Rationale**: Piping ensures zero buffering latency for the client. The accumulator only needs to hold a running token sum, not full message content.

**Alternative considered**: Buffer the full stream before forwarding — unacceptable UX; adds seconds of latency to every streaming call.

---

### 3. Lifecycle management via subprocess reference

**Decision**: A module-level variable holds the `subprocess.Popen` instance of the running `mitmproxy` process. `start()` is a no-op if the reference is not None; `stop()` calls `process.terminate()` and sets the reference to None.

**Rationale**: Matches the existing API spec requirement ("already running → return 200 with status running"). Simple and avoids PID-file complexity. Subprocess isolation ensures the FastAPI process remains stable if the proxy encounters an error.

---

### 4. Usage event schema alignment

**Decision**: Map proxy-extracted fields directly to the `usage_events` schema already defined in `data-persistence`: `input_tokens`, `output_tokens`, `thinking_tokens` (from `usage.thinking_tokens` or `usage.input_tokens_details.thinking_tokens`), `cache_creation_tokens`, `cache_read_tokens`, `source = "proxy"`.

**Rationale**: The persistence layer is the single source of truth; the proxy must not invent a parallel schema.

## Risks / Trade-offs

- **Client must opt in** → Clients must change their base URL to `http://localhost:8080`. No transparent OS-level interception. Mitigation: document clearly; consider future CONNECT-tunnel support as a separate capability.
- **Port conflict** → `8080` may be in use. Mitigation: surface `EADDRINUSE` as a clear error in the `/api/proxy/status` response; consider a configurable port in a future iteration.
- **SSE accumulator correctness** → Anthropic may change the field name or chunk structure. Mitigation: log raw final chunk on parse failure; emit a warning but do not drop the request.
- **No request authentication** → Any local process can call the proxy. Acceptable for a local-only desktop tool; revisit if the tool gains remote access features.

## Migration Plan

1. Deploy backend with proxy module included but proxy stopped by default.
2. Dashboard power button wires to `/api/proxy/start` and `/api/proxy/stop`.
3. No database migration required — usage events use the existing schema with `source = "proxy"`.
4. Rollback: remove proxy module; lifecycle endpoints return `501 Not Implemented`.

## Open Questions

- Should the proxy port be user-configurable via a settings file, or hardcoded to `8080` for v1?
- Are thinking tokens exposed in the top-level `usage` object or only inside `usage.input_tokens_details`? Need to verify against current Anthropic streaming spec.
