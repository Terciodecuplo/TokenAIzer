## 1. Project Setup

- [x] 1.1 Create `backend/` directory as the Python project root
- [x] 1.2 Create `backend/requirements.txt` with initial dependencies: `fastapi`, `uvicorn`, `mitmproxy`, `httpx`
- [x] 1.3 Create `backend/proxy/` package with `__init__.py`
- [x] 1.4 Create `backend/proxy/lifecycle.py` exporting `start()`, `stop()`, and `get_status()` functions
- [x] 1.5 Create `backend/proxy/interceptor.py` as the mitmproxy inline script

## 2. Core Proxy Server

- [x] 2.1 Implement mitmproxy startup in `lifecycle.py` spawning a `subprocess.Popen` instance on `localhost:8080`
- [x] 2.2 Configure mitmproxy to forward all requests to `api.anthropic.com` transparently
- [x] 2.3 Verify upstream response (status code + headers + body) is returned to the client unmodified
- [x] 2.4 Read the `model` field from the JSON request body in `interceptor.py`

## 3. Usage Extraction — Non-Streaming

- [x] 3.1 In `interceptor.py`, detect non-streaming responses by absence of `text/event-stream` content-type
- [x] 3.2 Parse the JSON response body to locate the `usage` object
- [x] 3.3 Extract `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, and `thinking_tokens` (default absent fields to `0`)
- [x] 3.4 Call the persistence layer to write the usage event with `source = "proxy"`

## 4. Streaming (SSE) Support

- [x] 4.1 Detect `content-type: text/event-stream` on the upstream response in `interceptor.py`
- [x] 4.2 Pass SSE chunks to the client immediately without buffering
- [x] 4.3 Implement an SSE accumulator that scans each chunk for a `usage` object
- [x] 4.4 On receipt of the `message_stop` event or stream close, extract accumulated token counts and persist the usage event
- [x] 4.5 Log a warning (and skip persistence) if the final chunk contains no parseable `usage` object

## 5. Lifecycle Management

- [x] 5.1 Implement `start()`: spawn mitmproxy subprocess and store the `Popen` reference; return `{ "status": "running", "port": 8080 }` if reference is already not None
- [x] 5.2 Implement `stop()`: call `process.terminate()`, set reference to None, return `{ "status": "stopped" }`
- [x] 5.3 Implement `get_status()`: return current state and port
- [x] 5.4 Ensure proxy subprocess is not started on backend startup; default state is stopped

## 6. REST API Wiring

- [x] 6.1 Create `backend/api/proxy.py` with FastAPI router for proxy lifecycle endpoints
- [x] 6.2 Wire `POST /api/proxy/start` to `lifecycle.start()` and return its result as JSON
- [x] 6.3 Wire `POST /api/proxy/stop` to `lifecycle.stop()` and return its result as JSON
- [x] 6.4 Wire `GET /api/proxy/status` to `lifecycle.get_status()` and return its result as JSON

## 7. Error Handling & Edge Cases

- [x] 7.1 Return a clear error response `{ "error": "port_in_use" }` if port 8080 is already occupied
- [x] 7.2 Handle upstream connection errors gracefully and return a `502 Bad Gateway` to the client
- [x] 7.3 Ensure `stop()` is idempotent when the proxy is already stopped
- [x] 7.4 Handle `mitmproxy` subprocess unexpected exit and update status to stopped automatically

## 8. Testing

- [x] 8.1 Write a unit test for the SSE accumulator (happy path + missing usage field)
- [x] 8.2 Write an integration test: start proxy → send a mocked non-streaming request → assert usage event persisted
- [x] 8.3 Write an integration test: start proxy → send a mocked streaming request → assert usage event persisted after stream closes
- [x] 8.4 Write tests for `start()`/`stop()` idempotency
- [x] 8.5 Verify `GET /api/proxy/status` returns correct state after each lifecycle transition
