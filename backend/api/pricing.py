from fastapi import APIRouter

from db.pricing import get_all_pricing

router = APIRouter(prefix="/api", tags=["pricing"])


@router.get("/pricing")
def get_pricing() -> list:
    return get_all_pricing()
