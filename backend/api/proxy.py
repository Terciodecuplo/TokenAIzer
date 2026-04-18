from fastapi import APIRouter

from proxy import lifecycle

router = APIRouter(prefix="/api/proxy", tags=["proxy"])


@router.post("/start")
def proxy_start() -> dict:
    return lifecycle.start()


@router.post("/stop")
def proxy_stop() -> dict:
    return lifecycle.stop()


@router.get("/status")
def proxy_status() -> dict:
    return lifecycle.get_status()
