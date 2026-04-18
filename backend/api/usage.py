from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from db.usage import get_usage_history, get_usage_summary, write_usage_event

router = APIRouter(prefix="/api/usage", tags=["usage"])


@router.get("/summary")
def usage_summary() -> dict:
    return get_usage_summary()


@router.get("/history")
def usage_history(
    model: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list:
    return get_usage_history(model=model, date_from=date_from, date_to=date_to,
                              source=source, limit=limit, offset=offset)


@router.post("/manual", status_code=201)
def usage_manual(payload: dict) -> dict:
    model = payload.get("model")
    if not model:
        raise HTTPException(status_code=400, detail="model is required")
    usage = {
        "input_tokens":          payload.get("input_tokens", 0),
        "output_tokens":         payload.get("output_tokens", 0),
        "thinking_tokens":       payload.get("thinking_tokens", 0),
        "cache_creation_tokens": payload.get("cache_creation_tokens", 0),
        "cache_read_tokens":     payload.get("cache_read_tokens", 0),
    }
    event_id = write_usage_event(model, usage, source="manual")
    return {"id": event_id, "status": "created"}
