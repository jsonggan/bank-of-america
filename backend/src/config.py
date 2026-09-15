from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    title: str = "Schema Dashboard API"
    version: str = "1.0.0"
    description: str = "Register schemas, ingest validated rows, and generate configured views."
