from fastapi import FastAPI
from app.api.endpoints import user_router
from app.api.endpoints import costs_and_earnings_router

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(user_router)
    app.include_router(costs_and_earnings_router)

    return app