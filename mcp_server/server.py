from __future__ import annotations

import json
import logging
import time
from typing import Any

from mcp.server.fastmcp import FastMCP

from application.db import init_db, seed_db
from application.errors import ApplicationError, error_payload
from application.service import (
    get_account_360 as app_get_account_360,
    get_lead_360 as app_get_lead_360,
    search_entities as app_search_entities,
)
from mcp_server.config import load_settings
from mcp_server.logging_utils import configure_logging


settings = load_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("mcp_server")

_BOOTSTRAPPED = False


def bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    init_db()
    seed_db()
    _BOOTSTRAPPED = True

mcp = FastMCP("ABC CRM/SFA MCP POC")


def _safe_error(message: str) -> dict[str, Any]:
    return error_payload(message, error_code="MCP_TOOL_ERROR", recoverable=True)


def _log_tool_call(tool_name: str, tool_input: dict[str, Any], duration_ms: int, success: bool, error_code: str = "") -> None:
    payload = {
        "tool_name": tool_name,
        "input": tool_input,
        "execution_time_ms": duration_ms,
        "success": success,
    }
    if error_code:
        payload["error_code"] = error_code
    logger.info(json.dumps(payload))


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return server health and DB path."""
    start = time.perf_counter()
    bootstrap()
    response = {"status": "ok", "env": settings.app_env, "db_path": settings.app_db_path}
    _log_tool_call("health_check", {}, int((time.perf_counter() - start) * 1000), True)
    return response


@mcp.tool()
def search_entities(query: str, entity_type: str) -> dict[str, Any]:
    """Search accounts or leads by query text."""
    start = time.perf_counter()
    bootstrap()
    entity_type_normalized = entity_type.strip().lower()
    try:
        results = app_search_entities(query=query, entity_type=entity_type_normalized)
        response = {"query": query, "entity_type": entity_type_normalized, "results": results}
        _log_tool_call(
            "search_entities",
            {"query": query, "entity_type": entity_type_normalized},
            int((time.perf_counter() - start) * 1000),
            True,
        )
        return response
    except ApplicationError as exc:
        logger.warning("Search failed: %s", exc)
        _log_tool_call(
            "search_entities",
            {"query": query, "entity_type": entity_type_normalized},
            int((time.perf_counter() - start) * 1000),
            False,
            "APPLICATION_ERROR",
        )
        return _safe_error(str(exc))


@mcp.tool()
def get_account_360(account_id: str) -> dict[str, Any]:
    """Get account 360 summary from application database."""
    start = time.perf_counter()
    bootstrap()
    try:
        response = app_get_account_360(account_id=account_id)
        _log_tool_call("get_account_360", {"account_id": account_id}, int((time.perf_counter() - start) * 1000), True)
        return response
    except ApplicationError as exc:
        logger.warning("Account 360 failed: %s", exc)
        _log_tool_call(
            "get_account_360",
            {"account_id": account_id},
            int((time.perf_counter() - start) * 1000),
            False,
            "APPLICATION_ERROR",
        )
        return _safe_error(str(exc))


@mcp.tool()
def get_lead_360(lead_id: str) -> dict[str, Any]:
    """Get lead 360 summary from application database."""
    start = time.perf_counter()
    bootstrap()
    try:
        response = app_get_lead_360(lead_id=lead_id)
        _log_tool_call("get_lead_360", {"lead_id": lead_id}, int((time.perf_counter() - start) * 1000), True)
        return response
    except ApplicationError as exc:
        logger.warning("Lead 360 failed: %s", exc)
        _log_tool_call(
            "get_lead_360",
            {"lead_id": lead_id},
            int((time.perf_counter() - start) * 1000),
            False,
            "APPLICATION_ERROR",
        )
        return _safe_error(str(exc))


if __name__ == "__main__":
    bootstrap()
    mcp.run(transport="stdio")

