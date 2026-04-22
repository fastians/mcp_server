# MCP Prompts

Use these prompts in an MCP client connected to `mcp_server.server`:

1. `Run health_check and confirm app/db is ready.`
2. `Search account entities for Acme.`
3. `Get account 360 for account_id acc_001 and list top risks and actions.`
4. `Get lead 360 for lead_id lead_001 and suggest the next three actions.`

Expected agent workflow:
- Call `health_check` to validate MCP and DB readiness.
- Call `search_entities` to resolve user text into IDs.
- Call `get_account_360` or `get_lead_360` with IDs.
- Use `sources` in the final response to keep it auditable.
