from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = "application/data/abc_crm.db"


def get_db_path() -> str:
    return os.getenv("APP_DB_PATH", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                status TEXT NOT NULL,
                owner TEXT NOT NULL,
                score INTEGER NOT NULL,
                last_activity_date TEXT,
                next_meeting TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                name TEXT NOT NULL,
                stage TEXT NOT NULL,
                value INTEGER NOT NULL,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                date TEXT NOT NULL,
                summary TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_account_id ON opportunities(account_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_entity ON activities(entity_type, entity_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)")
    conn.close()


def seed_db() -> None:
    conn = get_connection()
    with conn:
        account_count = conn.execute("SELECT COUNT(1) FROM accounts").fetchone()[0]
        if account_count > 0:
            return

        conn.execute("INSERT INTO accounts(id, name, industry) VALUES (?, ?, ?)", ("acc_001", "Acme Corp", "Manufacturing"))
        conn.execute("INSERT INTO accounts(id, name, industry) VALUES (?, ?, ?)", ("acc_002", "Globex Inc", "Technology"))

        conn.execute(
            """
            INSERT INTO leads(id, name, email, status, owner, score, last_activity_date, next_meeting)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("lead_001", "Priya Sharma", "priya@acme.com", "Working", "rep_17", 42, "2026-04-05", None),
        )
        conn.execute(
            """
            INSERT INTO leads(id, name, email, status, owner, score, last_activity_date, next_meeting)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("lead_002", "John Miller", "john@globex.com", "New", "rep_22", 68, "2026-04-19", "2026-04-25"),
        )

        conn.execute(
            "INSERT INTO opportunities(id, account_id, name, stage, value) VALUES (?, ?, ?, ?, ?)",
            ("opp_101", "acc_001", "ERP Expansion", "Qualification", 125000),
        )
        conn.execute(
            "INSERT INTO opportunities(id, account_id, name, stage, value) VALUES (?, ?, ?, ?, ?)",
            ("opp_102", "acc_001", "Renewal Q3", "Prospecting", 45000),
        )

        conn.execute(
            "INSERT INTO activities(id, entity_type, entity_id, activity_type, date, summary) VALUES (?, ?, ?, ?, ?, ?)",
            ("act_888", "account", "acc_001", "email", "2026-04-01", "Pricing follow-up sent."),
        )
        conn.execute(
            "INSERT INTO activities(id, entity_type, entity_id, activity_type, date, summary) VALUES (?, ?, ?, ?, ?, ?)",
            ("act_887", "account", "acc_001", "call", "2026-03-20", "Discovery call completed."),
        )
        conn.execute(
            "INSERT INTO activities(id, entity_type, entity_id, activity_type, date, summary) VALUES (?, ?, ?, ?, ?, ?)",
            ("act_901", "lead", "lead_001", "email", "2026-04-05", "Intro email sent."),
        )
    conn.close()

