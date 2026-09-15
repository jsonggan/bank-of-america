import math
from copy import deepcopy
from typing import Any

from backend.src.controllers.schema import SchemaController
from backend.src.controllers.validation import _require_name, _require_object
from backend.src.models.errors import ServiceError
from backend.src.models.store import MemoryStore


class DashboardController:
    def __init__(self, store: MemoryStore, schemas: SchemaController) -> None:
        self.store = store
        self.schemas = schemas

    def register_dashboard(self, definition: Any) -> dict[str, Any]:
        _require_object(definition)
        _require_name(definition.get("name"), "name")
        name = definition["name"]
        if name in (".", "..") or any(
            char in "/\\" or ord(char) < 32 or ord(char) == 127 for char in name
        ):
            raise ServiceError(
                422, "name", "Expected a single URL path segment without control characters"
            )
        if definition["name"] in self.store.dashboards:
            raise ServiceError(409, "name", "Dashboard already exists")
        _require_name(definition.get("schema"), "schema")
        schema = self.schemas.get_schema(definition["schema"])
        if not isinstance(definition.get("views"), list) or not definition["views"]:
            raise ServiceError(422, "views", "Expected a nonempty array")
        fields = {field["name"]: field for field in schema["fields"]}
        for index, view in enumerate(definition["views"]):
            _require_object(view, f"views[{index}]")
            if view.get("type") not in ("summary", "table"):
                raise ServiceError(422, f"views[{index}].type", "Expected summary or table")
            if view["type"] == "summary":
                if not isinstance(view.get("field"), str) or view["field"] not in fields:
                    raise ServiceError(422, f"views[{index}].field", "Unknown summary field")
                if view.get("aggregation") != "sum":
                    raise ServiceError(422, f"views[{index}].aggregation", "Only sum is supported")
                if fields[view["field"]]["type"] != "number":
                    raise ServiceError(422, f"views[{index}].field", "Sum requires a numeric field")
            if view["type"] == "table":
                if not isinstance(view.get("columns"), list) or not view["columns"]:
                    raise ServiceError(422, f"views[{index}].columns", "Expected a nonempty array")
                for column_index, column in enumerate(view["columns"]):
                    if not isinstance(column, str) or column not in fields:
                        raise ServiceError(
                            422, f"views[{index}].columns[{column_index}]", "Unknown table column"
                        )
        self.store.dashboards[definition["name"]] = deepcopy(definition)
        return definition

    def get_dashboard_config(self, name: str) -> dict[str, Any]:
        if name not in self.store.dashboards:
            raise ServiceError(404, "name", f"Unknown dashboard: {name}")
        return deepcopy(self.store.dashboards[name])

    def generate_dashboard(self, name: str) -> dict[str, Any]:
        configuration = self.get_dashboard_config(name)
        rows = self.schemas.get_rows(configuration["schema"])
        views = []
        for index, view in enumerate(configuration["views"]):
            if view["type"] == "summary":
                try:
                    value = sum(row[view["field"]] for row in rows if view["field"] in row)
                except OverflowError:
                    raise ServiceError(
                        422, f"views[{index}]", "Sum exceeds finite numeric range"
                    ) from None
                if isinstance(value, float) and not math.isfinite(value):
                    raise ServiceError(422, f"views[{index}]", "Sum exceeds finite numeric range")
                views.append({"type": "summary", "value": value})
            elif view["type"] == "table":
                views.append(
                    {
                        "type": "table",
                        "rows": [
                            {column: row[column] for column in view["columns"] if column in row}
                            for row in rows
                        ],
                    }
                )
        return {"views": views}
