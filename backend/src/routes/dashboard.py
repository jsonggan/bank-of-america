from typing import Any

from fastapi import APIRouter, Request

from backend.src.controllers.dashboard import DashboardController
from backend.src.routes.common.http import json_body, read_json


def create_router(service: DashboardController) -> APIRouter:
    router = APIRouter(tags=["Dashboards"])

    @router.post(
        "/dashboard",
        status_code=201,
        openapi_extra=json_body(
            {
                "name": "trade-dashboard",
                "schema": "trade",
                "views": [{"type": "summary", "field": "amount", "aggregation": "sum"}],
            }
        ),
    )
    async def register_dashboard(request: Request) -> dict[str, Any]:
        return service.register_dashboard(await read_json(request))

    @router.get("/dashboard/{name:path}")
    async def get_dashboard(name: str) -> dict[str, Any]:
        return service.generate_dashboard(name)

    return router
