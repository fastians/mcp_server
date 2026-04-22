from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from mcp_server.server import get_account_360, get_lead_360, search_entities


@dataclass
class AgentResult:
    ok: bool
    response: str
    raw: dict[str, Any]


def _is_error(payload: dict[str, Any]) -> bool:
    return "error" in payload


def _build_account_response(payload: dict[str, Any]) -> str:
    entity = payload["entity"]["name"]
    status = payload.get("status", "unknown")
    risks = payload.get("open_risks", [])
    actions = payload.get("next_actions", [])
    sources = payload.get("sources", [])
    return (
        f"Account {entity} is currently {status}. "
        f"Top risks: {', '.join(risks[:2]) if risks else 'none'}. "
        f"Next actions: {', '.join(actions[:3]) if actions else 'none'}. "
        f"Sources used: {', '.join(s['record_id'] for s in sources[:5]) if sources else 'none'}."
    )


def _build_lead_response(payload: dict[str, Any]) -> str:
    entity = payload["entity"]["name"]
    status = payload.get("status", "unknown")
    risks = payload.get("open_risks", [])
    actions = payload.get("next_actions", [])
    sources = payload.get("sources", [])
    return (
        f"Lead {entity} is currently {status}. "
        f"Top risks: {', '.join(risks[:2]) if risks else 'none'}. "
        f"Next actions: {', '.join(actions[:3]) if actions else 'none'}. "
        f"Sources used: {', '.join(s['record_id'] for s in sources[:5]) if sources else 'none'}."
    )


def run_agent_query(user_query: str) -> AgentResult:
    q = user_query.lower().strip()
    target_type = "lead" if "lead" in q else "account"
    keyword = "Acme" if "acme" in q else "Priya" if "priya" in q else ""

    if not keyword:
        return AgentResult(
            ok=False,
            response="I could not determine the target entity. Please include account/lead name.",
            raw={},
        )

    search_payload = search_entities(query=keyword, entity_type=target_type)
    if _is_error(search_payload):
        return AgentResult(ok=False, response=search_payload["error"]["message"], raw=search_payload)

    results = search_payload.get("results", [])
    if not results:
        return AgentResult(ok=False, response=f"No {target_type} found for '{keyword}'.", raw=search_payload)

    target_id = results[0]["id"]
    detail_payload = get_lead_360(target_id) if target_type == "lead" else get_account_360(target_id)
    if _is_error(detail_payload):
        return AgentResult(ok=False, response=detail_payload["error"]["message"], raw=detail_payload)

    response = _build_lead_response(detail_payload) if target_type == "lead" else _build_account_response(detail_payload)
    return AgentResult(ok=True, response=response, raw=detail_payload)


def main() -> None:
    examples = [
        "Summarize Acme account and suggest next actions",
        "Summarize lead Priya and give recommendations",
    ]
    for prompt in examples:
        result = run_agent_query(prompt)
        print(f"\nUSER: {prompt}")
        print(f"AGENT: {result.response}")
        print("RAW:")
        print(json.dumps(result.raw, indent=2) if result.raw else "{}")


if __name__ == "__main__":
    main()
