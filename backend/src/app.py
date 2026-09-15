from fastapi import FastAPI

from backend.src.config import AppConfig
from backend.src.routes import dashboard, schema
from backend.src.routes.common.errors import register_error_handlers
from backend.src.service import DashboardService


def create_app(
    service: DashboardService | None = None, *, config: AppConfig | None = None
) -> FastAPI:
    config = config if config is not None else AppConfig()
    service = service if service is not None else DashboardService()
    app = FastAPI(title=config.title, version=config.version, description=config.description)
    register_error_handlers(app)
    app.include_router(schema.create_router(service.schemas))
    app.include_router(dashboard.create_router(service.dashboards))
    return app
