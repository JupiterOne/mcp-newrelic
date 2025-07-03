"""
Observability utilities for New Relic MCP Server.

Provides structured logging, metrics, and monitoring capabilities.
"""

import logging
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any


class StructuredLogger:
    """Structured logging with consistent format"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        """Log info with structured data"""
        self.logger.info(self._format_message(message, kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning with structured data"""
        self.logger.warning(self._format_message(message, kwargs))

    def error(self, message: str, error: Exception | None = None, **kwargs):
        """Log error with structured data"""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
        self.logger.error(self._format_message(message, kwargs))

    @staticmethod
    def _format_message(message: str, data: dict[str, Any]) -> str:
        """Format message with structured data"""
        if not data:
            return message

        formatted_data = " ".join([f"{k}={v}" for k, v in data.items()])
        return f"{message} | {formatted_data}"


class PerformanceMonitor:
    """Monitors performance metrics"""

    def __init__(self):
        self.logger = StructuredLogger(__name__)

    @asynccontextmanager
    async def measure_duration(self, operation: str, **context):
        """Measure operation duration"""
        start_time = time.time()
        self.logger.info(f"Starting {operation}", **context)

        try:
            yield
            duration = time.time() - start_time
            self.logger.info(
                f"Completed {operation}", duration_ms=round(duration * 1000, 2), status="success", **context
            )
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed {operation}", duration_ms=round(duration * 1000, 2), status="error", error=e, **context
            )
            raise

    def log_api_call(self, endpoint: str, status_code: int, duration_ms: float, **context):
        """Log API call metrics"""
        self.logger.info(
            "API call completed", endpoint=endpoint, status_code=status_code, duration_ms=duration_ms, **context
        )


def performance_monitor(operation_name: str):
    """Decorator for monitoring function performance"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()

            # Extract context from function arguments
            context = {"function": func.__name__, "module": func.__module__}

            async with monitor.measure_duration(operation_name, **context):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
