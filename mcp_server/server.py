from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from application.db import init_db, seed_db
from application.service import (
    ApplicationError,
    get_account_360 as app_get_account_360,
    get_lead_360 as app_get_lead_360,
    search_entities as app_search_entities,
)
from mcp_server.config import load_settings
from mcp_server.logging_utils import configure_logging


settings = load_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("mcp_server")

init_db()
seed_db()

mcp = FastMCP("ABC CRM/SFA MCP POC")


def _safe_error(message: str) -> dict[str, Any]:
    return {"error": {"message": message, "type": "application_error"}}


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return server health and DB path."""
    return {"status": "ok", "env": settings.app_env, "db_path": settings.app_db_path}


@mcp.tool()
def search_entities(query: str, entity_type: str) -> dict[str, Any]:
    """Search accounts or leads by query text."""
    entity_type_normalized = entity_type.strip().lower()
    try:
        results = app_search_entities(query=query, entity_type=entity_type_normalized)
        return {"query": query, "entity_type": entity_type_normalized, "results": results}
    except ApplicationError as exc:
        logger.warning("Search failed: %s", exc)
        return _safe_error(str(exc))


@mcp.tool()
def get_account_360(account_id: str) -> dict[str, Any]:
    """Get account 360 summary from application database."""
    try:
        return app_get_account_360(account_id=account_id)
    except ApplicationError as exc:
        logger.warning("Account 360 failed: %s", exc)
        return _safe_error(str(exc))


@mcp.tool()
def get_lead_360(lead_id: str) -> dict[str, Any]:
    """Get lead 360 summary from application database."""
    try:
        return app_get_lead_360(lead_id=lead_id)
    except ApplicationError as exc:
        logger.warning("Lead 360 failed: %s", exc)
        return _safe_error(str(exc))


if __name__ == "__main__":
    mcp.run(transport="stdio")

