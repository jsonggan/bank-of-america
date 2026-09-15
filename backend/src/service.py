from typing import Any

from backend.src.controllers.dashboard import DashboardController
from backend.src.controllers.schema import SchemaController
from backend.src.models.store import MemoryStore


class DashboardService:
    """One in-memory store for serialized operations in a single worker."""

    def __init__(self) -> None:
        self._store = MemoryStore()
        self.schemas = SchemaController(self._store)
        self.dashboards = DashboardController(self._store, self.schemas)

    def register_schema(self, definition: Any) -> dict[str, Any]:
        return self.schemas.register_schema(definition)

    def get_schema(self, name: str) -> dict[str, Any]:
        return self.schemas.get_schema(name)

    def ingest(self, batch: Any) -> dict[str, Any]:
        return self.schemas.ingest(batch)

    def get_rows(self, schema: str) -> list[dict[str, Any]]:
        return self.schemas.get_rows(schema)

    def register_dashboard(self, definition: Any) -> dict[str, Any]:
        return self.dashboards.register_dashboard(definition)

    def get_dashboard_config(self, name: str) -> dict[str, Any]:
        return self.dashboards.get_dashboard_config(name)

    def generate_dashboard(self, name: str) -> dict[str, Any]:
        return self.dashboards.generate_dashboard(name)
