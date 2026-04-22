from __future__ import annotations

import re
import subprocess
import time
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application.db import get_connection, init_db, seed_db
from application.errors import ApplicationError, error_payload
from application.service import get_account_360, get_lead_360, search_entities

ROOT_DIR = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(title="ABC CRM Test API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search")
def search(query: str, entity_type: str) -> dict:
    try:
        results = search_entities(query=query, entity_type=entity_type)
        return {"query": query, "entity_type": entity_type, "results": results}
    except ApplicationError as exc:
        return error_payload(str(exc))


@app.get("/account/{account_id}/360")
def account_360(account_id: str) -> dict:
    try:
        return get_account_360(account_id=account_id)
    except ApplicationError as exc:
        return error_payload(str(exc))


@app.get("/lead/{lead_id}/360")
def lead_360(lead_id: str) -> dict:
    try:
        return get_lead_360(lead_id=lead_id)
    except ApplicationError as exc:
        return error_payload(str(exc))


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


@app.post("/qa/run-unit-tests")
def run_unit_tests() -> dict:
    start = time.perf_counter()
    completed = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        timeout=60,
    )
    duration_ms = int((time.perf_counter() - start) * 1000)
    combined_output = f"{completed.stdout}\n{completed.stderr}".strip()

    ran_match = re.search(r"Ran (\d+) tests?", combined_output)
    test_count = int(ran_match.group(1)) if ran_match else 0

    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "passed": completed.returncode == 0,
        "test_count": test_count,
        "duration_ms": duration_ms,
        "command": "python3 -m unittest discover -s tests -p test_*.py",
        "output": combined_output,
    }


@app.post("/qa/run-smoke-test")
def run_smoke_test() -> dict:
    start = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", ".")
    completed = subprocess.run(
        ["python3", "scripts/smoke_test.py"],
        cwd=str(ROOT_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    duration_ms = int((time.perf_counter() - start) * 1000)
    combined_output = f"{completed.stdout}\n{completed.stderr}".strip()

    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "passed": completed.returncode == 0,
        "duration_ms": duration_ms,
        "command": "python3 scripts/smoke_test.py",
        "output": combined_output,
    }

