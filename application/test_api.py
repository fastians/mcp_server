from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application.db import get_connection, init_db, seed_db
from application.service import ApplicationError, get_account_360, get_lead_360, search_entities


app = FastAPI(title="ABC CRM Test API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
seed_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search")
def search(query: str, entity_type: str) -> dict:
    try:
        results = search_entities(query=query, entity_type=entity_type)
        return {"query": query, "entity_type": entity_type, "results": results}
    except ApplicationError as exc:
        return {"error": {"type": "application_error", "message": str(exc)}}


@app.get("/account/{account_id}/360")
def account_360(account_id: str) -> dict:
    try:
        return get_account_360(account_id=account_id)
    except ApplicationError as exc:
        return {"error": {"type": "application_error", "message": str(exc)}}


@app.get("/lead/{lead_id}/360")
def lead_360(lead_id: str) -> dict:
    try:
        return get_lead_360(lead_id=lead_id)
    except ApplicationError as exc:
        return {"error": {"type": "application_error", "message": str(exc)}}


@app.get("/application-data")
def application_data() -> dict:
    with get_connection() as conn:
        accounts = [dict(row) for row in conn.execute("SELECT id, name, industry FROM accounts ORDER BY name").fetchall()]
        leads = [
            dict(row)
            for row in conn.execute(
                "SELECT id, name, email, status, owner, score, last_activity_date, next_meeting FROM leads ORDER BY name"
            ).fetchall()
        ]
        opportunities = [
            dict(row)
            for row in conn.execute(
                "SELECT id, account_id, name, stage, value FROM opportunities ORDER BY value DESC"
            ).fetchall()
        ]
        activities = [
            dict(row)
            for row in conn.execute(
                "SELECT id, entity_type, entity_id, activity_type, date, summary FROM activities ORDER BY date DESC"
            ).fetchall()
        ]
    return {
        "accounts": accounts,
        "leads": leads,
        "opportunities": opportunities,
        "activities": activities,
    }

