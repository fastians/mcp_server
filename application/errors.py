from __future__ import annotations

from typing import Any


class ApplicationError(Exception):
    """Raised when application layer cannot process a request."""


def error_payload(
    message: str,
    error_code: str = "APPLICATION_ERROR",
    recoverable: bool = True,
    error_type: str = "application_error",
) -> dict[str, Any]:
    return {
        "error": {
            "error_code": error_code,
            "message": message,
            "recoverable": recoverable,
            "type": error_type,
        }
    }

