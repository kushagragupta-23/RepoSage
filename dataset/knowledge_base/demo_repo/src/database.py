from dataclasses import dataclass
from .config import DATABASE_URL, DB_POOL_SIZE


@dataclass
class DatabaseSettings:
    url: str = DATABASE_URL
    pool_size: int = DB_POOL_SIZE
    connect_timeout_seconds: int = 5


def build_connection_options(settings: DatabaseSettings | None = None) -> dict:
    settings = settings or DatabaseSettings()
    return {
        "url": settings.url,
        "pool_size": settings.pool_size,
        "connect_timeout_seconds": settings.connect_timeout_seconds,
    }


def likely_connection_causes(error_message: str) -> list[str]:
    message = error_message.lower()
    causes = []
    if "timeout" in message:
        causes.extend(["database host unreachable", "connection pool exhausted"])
    if "authentication" in message or "password" in message:
        causes.append("database credentials rejected")
    if "name or service not known" in message or "dns" in message:
        causes.append("database hostname/DNS resolution failure")
    return causes or ["inspect the full driver error and database configuration"]
