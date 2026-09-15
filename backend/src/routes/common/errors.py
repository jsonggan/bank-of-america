from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from backend.src.models.errors import ServiceError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceError)
    async def service_error(request: Request, error: ServiceError) -> JSONResponse:
        return JSONResponse({"errors": error.details}, status_code=error.status)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException) -> JSONResponse:
        return JSONResponse(
            {"errors": [{"path": request.url.path, "reason": str(error.detail)}]},
            status_code=error.status_code,
            headers=error.headers,
        )
