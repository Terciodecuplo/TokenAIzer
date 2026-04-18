## 1. Backend — Exchange Rate Endpoint

- [x] 1.1 Create `backend/api/exchange_rate.py` with a FastAPI router exposing `GET /api/exchange-rate`; use `urllib.request.urlopen` to fetch Frankfurter; return `{"eur": float}` on success or `{"eur": null}` on any error
- [x] 1.2 Register the exchange rate router in `backend/main.py` (import and `app.include_router`)

## 2. Backend — Tests

- [x] 2.1 Add tests to `backend/tests/test_api_routes.py`: one test that monkeypatches the Frankfurter fetch to return a valid rate, one that monkeypatches it to raise an exception; assert response body in both cases

## 3. Frontend — Update Exchange Rate Fetch

- [x] 3.1 Update `dashboard/src/exchangeRate.js` to fetch from `/api/exchange-rate` instead of `https://api.frankfurter.app/latest?from=USD&to=EUR`; parse `data.eur` (instead of `data.rates?.EUR`) and set the store
