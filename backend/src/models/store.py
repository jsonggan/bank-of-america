from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryStore:
    schemas: dict[str, dict[str, Any]] = field(default_factory=dict)
    rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    dashboards: dict[str, dict[str, Any]] = field(default_factory=dict)
