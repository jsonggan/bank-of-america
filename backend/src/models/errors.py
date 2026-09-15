from typing import Any


class ServiceError(ValueError):
    def __init__(self, status: int, path: str, reason: str, **context: Any):
        super().__init__(reason)
        self.status = status
        self.details = [{"path": path, "reason": reason, **context}]
