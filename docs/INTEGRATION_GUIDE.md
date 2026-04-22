# Third-Party Integration Guide

This guide is intentionally practical. If you are integrating an external AI client, follow this doc only.

## 1) What You Need

- Python 3.10+
- Repo checked out
- Dependencies installed

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Start MCP Server

From repo root:

```bash
./mcp.sh
```

Equivalent:

```bash
PYTHONPATH=. python -m mcp_server.server
```

Transport is `stdio`.

## 3) Tool Surface (Contract)

Tool names:

- `health_check`
- `search_entities`
- `get_account_360`
- `get_lead_360`

### Required call order

1. `health_check()`
2. `search_entities(query, entity_type)`
3. `get_account_360(account_id)` or `get_lead_360(lead_id)`

Do not skip step 2. Always resolve IDs first.

## 4) Minimal Happy Path

User asks: "Summarize Acme account"

Agent should:

1. `search_entities("Acme", "account")`
2. pick `results[0].id` (example: `acc_001`)
3. `get_account_360("acc_001")`
4. answer using:
   - `health`
   - `open_risks`
   - `next_actions`
   - `sources`

## 5) Response Shape You Can Depend On

For `get_account_360` and `get_lead_360`:

```json
{
  "entity": {
    "type": "account|lead",
    "id": "string",
    "name": "string"
  },
  "summary": "string",
  "status": "healthy|attention|at_risk",
  "health": "green|amber|red",
  "open_risks": ["string"],
  "recent_activity": [
    {
      "id": "string",
      "type": "string",
      "date": "YYYY-MM-DD",
      "summary": "string"
    }
  ],
  "next_actions": ["string", "string", "string"],
  "sources": [
    {
      "record_type": "account|lead|opportunity|activity",
      "record_id": "string"
    }
  ]
}
```

## 6) Error Contract

All tool errors return:

```json
{
  "error": {
    "error_code": "string",
    "message": "string",
    "recoverable": true,
    "type": "application_error"
  }
}
```

Client rule:

- check `error` first
- if present, do not parse normal payload fields
- show/log `error.message`

## 7) Integration Checklist (Must Pass)

- MCP server starts without crash
- `health_check` returns `status: ok`
- `search_entities("Acme", "account")` returns at least one result
- `get_account_360` returns all six top-level fields
- `get_lead_360` returns all six top-level fields
- Invalid input returns `error` envelope (not traceback)

## 8) Quick Verification Commands

Run smoke test:

```bash
PYTHONPATH=. python scripts/smoke_test.py
```

Run unit tests:

```bash
PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py"
```

## 9) Known Scope (Important)

Current MCP scope is read-only.

- No write tools
- No per-user role auth
- SQLite sample-backed behavior

Integrate against current tool contract only.

## 10) Where to Look If Something Fails

- Tool implementation: `mcp_server/server.py`
- App query logic: `application/service.py`
- Summary logic: `application/summary.py`
- Full technical reference: `docs/MCP_DOCUMENTATION.md`
