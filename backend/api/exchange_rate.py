import json
import urllib.request
from fastapi import APIRouter

router = APIRouter()

_EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"


@router.get("/api/exchange-rate")
def get_exchange_rate():
    try:
        with urllib.request.urlopen(_EXCHANGE_RATE_URL, timeout=5) as resp:
            data = json.loads(resp.read())
        rate = data.get("rates", {}).get("EUR")
        return {"eur": float(rate) if rate is not None else None}
    except Exception:
        return {"eur": None}
