import logging
import httpx
from datetime import datetime, timezone
from typing import Any
from enum import Enum

from app.settings.config import settings

_stdlib = logging.getLogger(__name__)


class ELogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


async def _push(endpoint: str, payload: dict) -> None:
    """Fire-and-forget to app_logger_tracer. Never raises — logger failures must not affect the service."""
    if not settings.SERVICE_LOGGER_TRACER_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{settings.SERVICE_LOGGER_TRACER_URL}/v1/{endpoint}/",
                json=payload,
            )
    except Exception as e:
        _stdlib.warning("logger_tracer_service unreachable — log lost locally: %s", e)


class ServiceLogger:
    def __init__(self, service: str) -> None:
        self._service = service

    def _ts(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def info(self, message: str, event: str = "app.log", **ctx: Any) -> None:
        _stdlib.info(f"[{event}] {message}")
        await _push("logs", {
            "level": ELogLevel.INFO,
            "event": event,
            "message": message,
            "service": self._service,
            "environment": settings.ENVIRONMENT,
            "metadata": ctx,
        })

    async def warning(self, message: str, event: str = "app.warning", **ctx: Any) -> None:
        _stdlib.warning(f"[{event}] {message}")
        await _push("logs", {
            "level": ELogLevel.WARNING,
            "event": event,
            "message": message,
            "service": self._service,
            "environment": settings.ENVIRONMENT,
            "metadata": ctx,
        })

    async def error(self, message: str, event: str = "app.error", **ctx: Any) -> None:
        _stdlib.error(f"[{event}] {message}")
        await _push("logs", {
            "level": ELogLevel.ERROR,
            "event": event,
            "message": message,
            "service": self._service,
            "environment": settings.ENVIRONMENT,
            "metadata": ctx,
        })

    async def event(self, event_name: str, session_id: str = "system", **ctx: Any) -> None:
        _stdlib.info(f"[EVENT] {event_name}")
        await _push("events", {
            "event": event_name,
            "service": self._service,
            "session_id": session_id,
            "metadata": ctx,
        })

    async def metric(self, name: str, value: float, metric_type: str = "counter", labels: dict | None = None, **ctx: Any) -> None:
        _stdlib.info(f"[METRIC] {name}={value}")
        await _push("metrics", {
            "name": name,
            "value": value,
            "type": metric_type,
            "service": self._service,
            "labels": labels or {},
            "metadata": ctx,
        })


logger = ServiceLogger(service="dh_auth")
