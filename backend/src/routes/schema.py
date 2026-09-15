from typing import Any

from fastapi import APIRouter, Request

from backend.src.controllers.schema import SchemaController
from backend.src.routes.common.http import json_body, read_json


def create_router(service: SchemaController) -> APIRouter:
    router = APIRouter(tags=["Schemas and ingestion"])

    @router.post(
        "/schema",
        status_code=201,
        openapi_extra=json_body(
            {"name": "trade", "fields": [{"name": "amount", "type": "number", "required": True}]}
        ),
    )
    async def register_schema(request: Request) -> dict[str, Any]:
        return service.register_schema(await read_json(request))

    @router.post(
        "/ingest", openapi_extra=json_body({"schema": "trade", "rows": [{"amount": 1000}]})
    )
    async def ingest(request: Request) -> dict[str, Any]:
        return service.ingest(await read_json(request))

    return router
