# ABC CRM/SFA MCP POC (Simple)

Full MCP documentation:

- `docs/MCP_DOCUMENTATION.md`
- `docs/INTEGRATION_GUIDE.md` (for third-party integrators)
- `docs/ENGINEERING_REVIEW.md` (review findings + refactor notes)
- `docs/MCP_IMPLEMENTATION_CHECKLIST.md` (checklist compliance status)

This repo is organized into 3 clean parts:

1. `application/` - real application layer with SQLite database and seed data
2. `mcp_server/` - MCP server layer exposing tools
3. `ui/` + `scripts/` - UI testing and CLI smoke tests

Each part has a clear responsibility:
- `application` can be tested directly without MCP.
- `mcp_server` does not contain business tables; it calls `application`.
- `scripts` provides CLI smoke tests and MCP prompt checklist.

## Folder structure

- `application/db.py`: create SQLite tables and seed sample data
- `application/service.py`: application business reads (account/lead/search)
- `application/summary.py`: simple rule-based 360 summary logic
- `mcp_server/server.py`: MCP tools (`health_check`, `search_entities`, `get_account_360`, `get_lead_360`)
- `scripts/smoke_test.py`: end-to-end smoke test (AI agent simulation)
- `scripts/mcp_prompts.md`: prompts for MCP client demo
- `ui/`: React + Tailwind testing UI

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 1) Run the Application

The application layer is SQLite-based (`application/`) and is auto-initialized by the MCP server.
If DB file does not exist, it is created and seeded automatically.

Default database:

- `application/data/abc_crm.db` (or `APP_DB_PATH` from env)

Optional: inspect seeded data manually from SQLite:

```bash
sqlite3 application/data/abc_crm.db "SELECT id, name FROM accounts;"
sqlite3 application/data/abc_crm.db "SELECT id, name, status FROM leads;"
```

## 2) Explore the MCP Server

Start MCP server (stdio transport):

```bash
PYTHONPATH=. python -m mcp_server.server
```

Available tools:

- `health_check`
- `search_entities(query, entity_type)`
- `get_account_360(account_id)`
- `get_lead_360(lead_id)`

What each tool does:

- `health_check`: confirms server is up and DB path is configured
- `search_entities`: resolves user text to account/lead IDs
- `get_account_360`: returns structured account summary with risks/actions/sources
- `get_lead_360`: returns structured lead summary with risks/actions/sources

## 3) Test MCP Server (User Testing Flow)

### A. Quick local smoke test (recommended first)

Run end-to-end local usage script:

```bash
PYTHONPATH=. python scripts/smoke_test.py
```

This script simulates AI-agent style usage:
1. Agent checks `health_check`
2. Agent resolves entity id with `search_entities`
3. Agent calls `get_account_360` or `get_lead_360`
4. Agent reads `open_risks`, `next_actions`, and `sources` for grounded response

### B. MCP client prompt testing

Use prompts from:

- `scripts/mcp_prompts.md`

Suggested order:
1. Run `health_check`
2. Search for account/lead IDs
3. Fetch 360 summary
4. Validate output fields and source references

### C. What user should validate

- Response has required schema fields:
  - `entity`, `summary`, `status`, `health`, `open_risks`, `recent_activity`, `next_actions`, `sources`
- `next_actions` contains at least 3 actions
- `sources` includes record IDs used to ground output
- Invalid input returns safe error format (no traceback)

## Unit tests

```bash
PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py"
```

## Complete test checklist

1. Setup completes without errors (`venv`, install, `.env`)
2. DB file is created at `application/data/abc_crm.db`
3. MCP server starts successfully
4. `scripts/smoke_test.py` prints all 4 steps with valid JSON
5. Unit tests pass
6. MCP prompts in `scripts/mcp_prompts.md` work in client

## UI testing (React + Tailwind)

This repo includes a basic UI for manual testing:

- `ui/` (React + Tailwind + Vite)

### Start backend API for UI

From project root:

```bash
PYTHONPATH=. uvicorn application.test_api:app --reload --port 8000
```

### Start UI

In a second terminal:

```bash
cd ui
npm install
npm run dev
```

Open the local URL shown by Vite (usually `http://127.0.0.1:5173`).

### Helper run scripts

From repo root:

```bash
./be.sh   # backend API
./fe.sh   # frontend UI
./mcp.sh  # MCP server (stdio)
./all.sh  # run all three together (with logs)
```

`all.sh` writes logs to `.run_logs/`.

### How user tests from UI

1. Click `Run health_check`
2. Run `search_entities` for account/lead
3. Run `get_account_360`
4. Run `get_lead_360`
5. Open `Test Status` tab and click `Run Unit Tests` and `Run Smoke Test`
6. Validate JSON includes:
   - `entity`, `summary`, `status`, `health`, `open_risks`, `recent_activity`, `next_actions`, `sources`
