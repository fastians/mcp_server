from __future__ import annotations

from typing import Any

from application.db import get_connection
from application.errors import ApplicationError
from application.summary import compose_account_360, compose_lead_360


def _validate_non_empty(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ApplicationError(f"{field_name} must be a non-empty string")
    return normalized


def search_entities(query: str, entity_type: str) -> list[dict[str, Any]]:
    normalized_query = _validate_non_empty(query, "query")
    normalized_entity_type = _validate_non_empty(entity_type, "entity_type").lower()
    term = f"%{normalized_query.lower()}%"
    with get_connection() as conn:
        if normalized_entity_type == "account":
            rows = conn.execute(
                "SELECT id, name FROM accounts WHERE lower(name) LIKE ? OR lower(id) LIKE ? ORDER BY name",
                (term, term),
            ).fetchall()
            return [{"id": row["id"], "name": row["name"]} for row in rows]
        if normalized_entity_type == "lead":
            rows = conn.execute(
                "SELECT id, name, email FROM leads WHERE lower(name) LIKE ? OR lower(id) LIKE ? OR lower(email) LIKE ? ORDER BY name",
                (term, term, term),
            ).fetchall()
            return [{"id": row["id"], "name": row["name"], "email": row["email"]} for row in rows]
    raise ApplicationError("entity_type must be one of: account, lead")


def get_account_360(account_id: str) -> dict[str, Any]:
    normalized_account_id = _validate_non_empty(account_id, "account_id")
    with get_connection() as conn:
        account_row = conn.execute("SELECT id, name, industry FROM accounts WHERE id = ?", (normalized_account_id,)).fetchone()
        if not account_row:
            raise ApplicationError(f"Account not found: {normalized_account_id}")

        opportunities = conn.execute(
            "SELECT id, name, stage, value FROM opportunities WHERE account_id = ? ORDER BY value DESC",
            (normalized_account_id,),
        ).fetchall()
        activities = conn.execute(
            """
            SELECT id, activity_type, date, summary
            FROM activities
            WHERE entity_type = 'account' AND entity_id = ?
            ORDER BY date DESC
            """,
            (normalized_account_id,),
        ).fetchall()

    payload = {
        "id": account_row["id"],
        "name": account_row["name"],
        "industry": account_row["industry"],
        "open_opportunities": [
            {"id": row["id"], "name": row["name"], "stage": row["stage"], "value": row["value"]} for row in opportunities
        ],
        "recent_activities": [
            {"id": row["id"], "type": row["activity_type"], "date": row["date"], "summary": row["summary"]}
            for row in activities
        ],
        "sources": [{"record_type": "account", "record_id": normalized_account_id}]
        + [{"record_type": "opportunity", "record_id": row["id"]} for row in opportunities]
        + [{"record_type": "activity", "record_id": row["id"]} for row in activities],
    }
    return compose_account_360(payload)


def get_lead_360(lead_id: str) -> dict[str, Any]:
    normalized_lead_id = _validate_non_empty(lead_id, "lead_id")
    with get_connection() as conn:
        lead_row = conn.execute(
            "SELECT id, name, email, status, owner, score, last_activity_date, next_meeting FROM leads WHERE id = ?",
            (normalized_lead_id,),
        ).fetchone()
        if not lead_row:
            raise ApplicationError(f"Lead not found: {normalized_lead_id}")

        activities = conn.execute(
            """
            SELECT id, activity_type, date, summary
            FROM activities
            WHERE entity_type = 'lead' AND entity_id = ?
            ORDER BY date DESC
            """,
            (normalized_lead_id,),
        ).fetchall()

    payload = {
        "id": lead_row["id"],
        "name": lead_row["name"],
        "email": lead_row["email"],
        "status": lead_row["status"],
        "owner": lead_row["owner"],
        "score": lead_row["score"],
        "last_activity_date": lead_row["last_activity_date"],
        "next_meeting": lead_row["next_meeting"],
        "recent_activities": [
            {"id": row["id"], "type": row["activity_type"], "date": row["date"], "summary": row["summary"]}
            for row in activities
        ],
        "sources": [{"record_type": "lead", "record_id": normalized_lead_id}]
        + [{"record_type": "activity", "record_id": row["id"]} for row in activities],
    }
    return compose_lead_360(payload)

