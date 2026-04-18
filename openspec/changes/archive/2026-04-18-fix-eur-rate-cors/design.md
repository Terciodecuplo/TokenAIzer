## Context

The dashboard's `exchangeRate.js` currently calls `https://api.frankfurter.app/latest?from=USD&to=EUR` directly from the browser. Frankfurter does not include an `Access-Control-Allow-Origin` header permitting `localhost` origins, so the fetch is blocked by the browser's CORS policy. The EUR rate silently falls back to `null` and the dashboard shows "EUR rate unavailable" permanently.

The fix is a thin server-side proxy: the FastAPI backend fetches Frankfurter (server-to-server, no CORS constraint) and re-exposes the rate under `/api/exchange-rate`. The frontend calls its own origin and the CORS problem disappears.

## Goals / Non-Goals

**Goals:**
- Eliminate the CORS failure by routing the Frankfurter request through the backend
- Keep the frontend change minimal (one URL string change in `exchangeRate.js`)
- Add a backend test for the new endpoint

**Non-Goals:**
- Caching the exchange rate (out of scope; fetched fresh on each request)
- Supporting currencies other than EUR
- Storing historical exchange rates

## Decisions

### 1. Use `urllib.request` instead of `httpx` for the server-side fetch

**Decision**: Use Python's built-in `urllib.request.urlopen` in the new endpoint.

**Rationale**: `httpx` is listed as a *test* dependency (for `TestClient`). Using it in production code would require adding it to `requirements.txt` as a runtime dependency. `urllib.request` is in the standard library and sufficient for a single synchronous GET with a short timeout. FastAPI runs the route in a thread pool when the function is not `async`, so blocking is acceptable here.

**Alternative considered**: `httpx.get()` — cleaner API but adds a runtime dep. `requests` — another external dep, same concern.

### 2. Return `{ "eur": <float | null> }` from the endpoint

**Decision**: The endpoint always returns 200 with `{ "eur": <rate> }` or `{ "eur": null }` on failure.

**Rationale**: The frontend already handles `null` gracefully (shows "EUR rate unavailable"). Returning a non-200 status from the proxy would require additional error handling in `exchangeRate.js`. A uniform 200 with nullable payload is simpler.

### 3. Place the route in `backend/api/exchange_rate.py`

**Decision**: New file following the existing module-per-resource convention.

**Rationale**: Keeps parity with `proxy.py`, `usage.py`, and `pricing.py`. The router is registered in `main.py` the same way as other routers.

## Risks / Trade-offs

- **Frankfurter downtime** → Returns `{ "eur": null }`; dashboard degrades gracefully to USD-only display. No retry logic needed at this scale.
- **Latency added to dashboard load** → The EUR fetch is called once on mount, in parallel with other fetches. An extra ~100–300 ms round-trip to Frankfurter is acceptable.
- **Rate limiting** → Frankfurter's free tier is generous; one request per page load from a local tool is far below any limit.
