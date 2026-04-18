from fastapi import APIRouter

from db.database import get_connection

router = APIRouter(prefix="/api", tags=["pricing"])


@router.get("/pricing")
def get_pricing() -> list:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM model_pricing").fetchall()
    return [dict(r) for r in rows]
