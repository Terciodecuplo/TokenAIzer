from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Query

from db.usage import get_usage_breakdown

router = APIRouter()


def _period_to_dates(period: str) -> tuple[Optional[str], Optional[str]]:
    now = datetime.now(timezone.utc)
    if period == "today":
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        return date_from, None
    if period == "7d":
        return (now - timedelta(days=7)).isoformat(), None
    if period == "30d":
        return (now - timedelta(days=30)).isoformat(), None
    return None, None  # "all"


@router.get("/api/usage/breakdown")
def usage_breakdown(
    model: str = Query(...),
    period: str = Query("all"),
):
    date_from, date_to = _period_to_dates(period)
    result = get_usage_breakdown(model, date_from, date_to)
    result["period"] = period
    return result
