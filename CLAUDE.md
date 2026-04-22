# CLAUDE.md

This file provides instructions for AI coding agents working in this repository.

## Project overview

This is a simple ABC CRM/SFA MCP POC with 3 independent layers:

1. `application/` - SQLite-backed business application layer
2. `mcp_server/` - MCP server exposing tools
3. `ui/` and `scripts/` - UI/manual testing and script-based smoke testing

Primary goal: keep things simple and demo-friendly.

## Repository structure

- `application/db.py` - DB init and seed data
- `application/service.py` - app business reads and 360 payload assembly
- `application/summary.py` - rule-based summary composition
- `application/test_api.py` - FastAPI endpoints for UI testing
- `mcp_server/server.py` - MCP tools (`health_check`, `search_entities`, `get_account_360`, `get_lead_360`)
- `scripts/smoke_test.py` - local smoke test simulating AI agent usage
- `scripts/mcp_prompts.md` - MCP prompt sequence for manual validation
- `ui/` - React + Tailwind testing UI

## Run commands

Use these from repo root:

- Backend API: `./be.sh`
- Frontend UI: `./fe.sh`
- MCP server: `./mcp.sh`
- All services: `./all.sh`

Direct commands (if needed):

- Tests: `PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py"`
- Smoke test: `PYTHONPATH=. python scripts/smoke_test.py`
- Backend API direct: `PYTHONPATH=. uvicorn application.test_api:app --reload --port 8000`
- UI dev direct: `npm --prefix ui run dev`

## Agent expectations

- Prefer minimal, incremental changes.
- Keep architecture separation:
  - business logic in `application/`
  - tool exposure in `mcp_server/`
  - test/demo logic in `ui/` or `scripts/`
- Do not move business rules into UI or MCP wrappers.
- Preserve stable response schema:
  - `entity`, `health`, `open_risks`, `recent_activity`, `next_actions`, `sources`
- Keep errors safe and user-readable (no stack trace responses in API payloads).

## Coding guidelines

- Python:
  - Keep functions small and explicit.
  - Prefer standard library unless dependency is necessary.
  - Use clear names; avoid over-abstraction.
- React UI:
  - Keep state local and simple.
  - Prefer plain Tailwind utility classes over complex component frameworks.
- Docs:
  - Update `README.md` whenever commands or workflow change.

## Verification checklist after changes

1. Run unit tests:
   - `PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py"`
2. Run smoke flow:
   - `PYTHONPATH=. python scripts/smoke_test.py`
3. If UI touched, build UI:
   - `npm --prefix ui run build`
4. Confirm no accidental break in scripts:
   - `bash -n be.sh fe.sh mcp.sh all.sh`

## Out of scope unless requested

- Heavy auth/permissions systems
- Complex deployment setup
- Replacing SQLite with production DB
- Expanding beyond POC simplicity

