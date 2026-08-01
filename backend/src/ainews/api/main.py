from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ainews.api.routes import router as api_router
from ainews.core.config.settings import settings
from ainews.core.utils.logger import logger

app = FastAPI(
    title="AINEWS API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "Validation error on %s %s from %s: %s",
        request.method,
        request.url.path,
        request.client.host if request.client else "unknown",
        exc.errors(),
    )

    formatted_errors = []

    for err in exc.errors():
        field_name = str(err["loc"][-1]).replace("_", " ").capitalize()

        if err.get("input") is None:
            msg = f"{field_name} cannot be empty"
        else:
            msg = err["msg"].removeprefix("Value error, ")

        formatted_errors.append(
            {
                "type": err["type"],
                "loc": err["loc"],
                "msg": msg,
                "input": err.get("input"),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors},
    )


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s from %s",
        request.method,
        request.url.path,
        request.client.host if request.client else "unknown",
        exc_info=exc,
    )

    origin = request.headers.get("origin")
    headers = {}

    if origin in settings.cors_allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        if settings.cors_allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
        headers=headers,
    )
