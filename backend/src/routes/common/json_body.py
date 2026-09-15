import json
import math
from typing import Any


def _finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("Expected a finite JSON number")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def loads(value: str | bytes) -> Any:
    return json.loads(
        value,
        parse_constant=_finite_float,
        parse_float=_finite_float,
        object_pairs_hook=_unique_object,
    )
