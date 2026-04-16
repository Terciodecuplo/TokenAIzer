## 1. Project Setup

- [ ] 1.1 Add an HTTP proxy dependency (e.g. `node-http-proxy` or verify raw `http`/`https` modules suffice) to `package.json`
- [ ] 1.2 Create `src/proxy/index.js` (or `.ts`) as the proxy module entry point
- [ ] 1.3 Create `src/proxy/lifecycle.js` exporting `start()`, `stop()`, and `getStatus()` functions

## 2. Core Proxy Server

- [ ] 2.1 Implement the HTTP server in `src/proxy/index.js` that listens on `localhost:8080`
- [ ] 2.2 Forward non-streaming requests to `api.anthropic.com`, preserving method, headers, and body
- [ ] 2.3 Return the upstream response (status code + headers + body) to the client unmodified
- [ ] 2.4 Read the `model` field from the JSON request body for each intercepted request

## 3. Usage Extraction — Non-Streaming

- [ ] 3.1 Parse the JSON response body to locate the `usage` object
- [ ] 3.2 Extract `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, and thinking tokens (default absent fields to `0`)
- [ ] 3.3 Call the persistence layer to write the usage event with `source = "proxy"`

## 4. Streaming (SSE) Support

- [ ] 4.1 Detect `content-type: text/event-stream` on the upstream response
- [ ] 4.2 Pipe SSE chunks to the client immediately without buffering
- [ ] 4.3 Implement an SSE accumulator that scans each chunk for a `usage` object
- [ ] 4.4 On receipt of the `[DONE]` sentinel or stream close, extract accumulated token counts and persist the usage event
- [ ] 4.5 Log a warning (and skip persistence) if the final chunk contains no parseable `usage` object

## 5. Lifecycle Management

- [ ] 5.1 Implement `start()`: create and store the `http.Server` instance; return `{ status: "running", port: 8080 }` if already running
- [ ] 5.2 Implement `stop()`: call `server.close()`, null the reference, return `{ status: "stopped" }`
- [ ] 5.3 Implement `getStatus()`: return current state and port
- [ ] 5.4 Ensure proxy is stopped by default when the backend process starts

## 6. REST API Wiring

- [ ] 6.1 Wire `POST /api/proxy/start` to `lifecycle.start()` and return its result as JSON
- [ ] 6.2 Wire `POST /api/proxy/stop` to `lifecycle.stop()` and return its result as JSON
- [ ] 6.3 Wire `GET /api/proxy/status` to `lifecycle.getStatus()` and return its result as JSON

## 7. Error Handling & Edge Cases

- [ ] 7.1 Return a clear error response (`{ error: "EADDRINUSE" }`) if port 8080 is already occupied
- [ ] 7.2 Handle upstream connection errors gracefully and return a `502 Bad Gateway` to the client
- [ ] 7.3 Ensure `stop()` is idempotent when the proxy is already stopped

## 8. Testing

- [ ] 8.1 Write a unit test for the SSE accumulator (happy path + missing usage field)
- [ ] 8.2 Write an integration test: start proxy → send a mocked non-streaming request → assert usage event persisted
- [ ] 8.3 Write an integration test: start proxy → send a mocked streaming request → assert usage event persisted after stream closes
- [ ] 8.4 Write tests for `start()`/`stop()` idempotency
- [ ] 8.5 Verify `GET /api/proxy/status` returns correct state after each lifecycle transition
