from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.breakdown import router as breakdown_router
from api.exchange_rate import router as exchange_rate_router
from api.pricing import router as pricing_router
from api.proxy import router as proxy_router
from api.usage import router as usage_router
from db.database import init_db

app = FastAPI(title="TokenAIzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(breakdown_router)
app.include_router(exchange_rate_router)
app.include_router(proxy_router)
app.include_router(usage_router)
app.include_router(pricing_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
