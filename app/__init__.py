from fastapi import FastAPI, Request
from app.api.endpoints import user_router
from app.api.endpoints import costs_and_earnings_router
from app.api.endpoints import templates_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(user_router)
    app.include_router(costs_and_earnings_router)
    app.include_router(templates_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error = exc.errors()[0]

        if error["type"] == "missing" and error["loc"][0] == "cookie" and error["loc"][1] == "Authorization":
            return RedirectResponse('/login')

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": exc.errors()}),
        )

    return app
