from typing import Any

from fastapi import Request

from backend.src.models.errors import ServiceError
from backend.src.routes.common.json_body import loads


async def read_json(request: Request) -> Any:
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "application/json" and not (
        media_type.startswith("application/") and media_type.endswith("+json")
    ):
        raise ServiceError(422, "$", "Expected application/json content type")
    try:
        return loads(await request.body())
    except (ValueError, UnicodeError):
        raise ServiceError(
            422, "$", "Expected valid JSON with unique keys and finite numbers"
        ) from None


def json_body(example: dict[str, Any]) -> dict[str, Any]:
    """Document the JSON body; dynamic schema validation belongs to the service."""
    return {
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": {"type": "object"}, "example": example}},
        }
    }
