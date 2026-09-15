import math
from copy import deepcopy
from typing import Any

from backend.src.controllers.validation import _require_name, _require_object
from backend.src.models.errors import ServiceError
from backend.src.models.store import MemoryStore


class SchemaController:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def register_schema(self, definition: Any) -> dict[str, Any]:
        _require_object(definition)
        _require_name(definition.get("name"), "name")
        if definition["name"] in self.store.schemas:
            raise ServiceError(409, "name", "Schema already exists")
        if not isinstance(definition.get("fields"), list) or not definition["fields"]:
            raise ServiceError(422, "fields", "Expected a nonempty array")
        names = set()
        for index, field in enumerate(definition["fields"]):
            _require_object(field, f"fields[{index}]")
            _require_name(field.get("name"), f"fields[{index}].name")
            if field["name"] in names:
                raise ServiceError(422, f"fields[{index}].name", "Duplicate field")
            if "required" in field and not isinstance(field["required"], bool):
                raise ServiceError(422, f"fields[{index}].required", "Expected a boolean")
            names.add(field["name"])
            if field.get("type") not in ("string", "number"):
                raise ServiceError(422, f"fields[{index}].type", "Expected string or number")
        self.store.schemas[definition["name"]] = deepcopy(definition)
        self.store.rows[definition["name"]] = []
        return definition

    def get_schema(self, name: str) -> dict[str, Any]:
        if name not in self.store.schemas:
            raise ServiceError(404, "schema", f"Unknown schema: {name}")
        return deepcopy(self.store.schemas[name])

    def ingest(self, batch: Any) -> dict[str, Any]:
        _require_object(batch)
        _require_name(batch.get("schema"), "schema")
        schema = self.get_schema(batch["schema"])
        if not isinstance(batch.get("rows"), list):
            raise ServiceError(422, "rows", "Expected an array")
        allowed = {field["name"] for field in schema["fields"]}
        for index, row in enumerate(batch["rows"]):
            if not isinstance(row, dict):
                raise ServiceError(422, f"rows[{index}]", "Expected an object", row=index)
            for name in row:
                if name not in allowed:
                    raise ServiceError(
                        422, f"rows[{index}].{name}", "Unknown field", row=index, field=name
                    )
            for field in schema["fields"]:
                name = field["name"]
                if field.get("required", False) and name not in row:
                    raise ServiceError(
                        422,
                        f"rows[{index}].{name}",
                        "Missing required field",
                        row=index,
                        field=name,
                    )
                if name in row and field["type"] == "string" and not isinstance(row[name], str):
                    raise ServiceError(
                        422, f"rows[{index}].{name}", "Expected a string", row=index, field=name
                    )
                if (
                    name in row
                    and field["type"] == "number"
                    and type(row[name]) not in (int, float)
                ):
                    raise ServiceError(
                        422, f"rows[{index}].{name}", "Expected a number", row=index, field=name
                    )
                if name in row and isinstance(row[name], float) and not math.isfinite(row[name]):
                    raise ServiceError(
                        422,
                        f"rows[{index}].{name}",
                        "Expected a finite number",
                        row=index,
                        field=name,
                    )
        # Commit once, only after the entire batch has validated.
        self.store.rows[schema["name"]].extend(deepcopy(batch["rows"]))
        return {"accepted": len(batch["rows"])}

    def get_rows(self, schema: str) -> list[dict[str, Any]]:
        self.get_schema(schema)
        return deepcopy(self.store.rows[schema])
