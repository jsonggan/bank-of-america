from typing import Any

from backend.src.models.errors import ServiceError


def _require_object(value: Any, path: str = "$") -> None:
    if not isinstance(value, dict):
        raise ServiceError(422, path, "Expected an object")


def _require_name(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(422, path, "Expected a nonblank string")
