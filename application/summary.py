from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _days_since(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now(UTC) - date_obj.replace(tzinfo=UTC)).days
    except ValueError:
        return None


def compose_account_360(account: dict[str, Any]) -> dict[str, Any]:
    risks: list[str] = []
    next_actions: list[str] = []
    opportunities = account.get("open_opportunities", [])
    activities = account.get("recent_activities", [])

    if not opportunities:
        risks.append("No open opportunities on this account.")
        next_actions.append("Create or qualify at least one opportunity.")

    if opportunities:
        early_stage = [o for o in opportunities if o.get("stage") in {"Prospecting", "Qualification"}]
        if len(early_stage) == len(opportunities):
            risks.append("All open opportunities are in early stages.")
            next_actions.append("Schedule discovery calls with decision makers.")

    if not activities:
        risks.append("No recent engagement activity found.")
        next_actions.append("Plan follow-up email and call sequence this week.")
    else:
        days = _days_since(activities[0].get("date"))
        if days is not None and days > 14:
            risks.append("Last activity is older than two weeks.")
            next_actions.append("Re-engage with a tailored outreach update.")

    health = "green" if not risks else ("amber" if len(risks) == 1 else "red")
    status = {"green": "healthy", "amber": "attention", "red": "at_risk"}[health]

    while len(next_actions) < 3:
        next_actions.append(
            [
                "Review top contacts and define multi-thread plan.",
                "Validate expected close dates with owners.",
                "Capture blockers and assign next step owners.",
            ][len(next_actions)]
        )

    return {
        "entity": {"type": "account", "id": account.get("id"), "name": account.get("name")},
        "summary": f"Account {account.get('name')} is {status} with {len(risks)} open risk(s).",
        "status": status,
        "health": health,
        "open_risks": risks,
        "recent_activity": activities[:5],
        "next_actions": next_actions[:3],
        "sources": account.get("sources", []),
    }


def compose_lead_360(lead: dict[str, Any]) -> dict[str, Any]:
    risks: list[str] = []
    next_actions: list[str] = []

    last_touch_days = _days_since(lead.get("last_activity_date"))
    if last_touch_days is None or last_touch_days > 10:
        risks.append("Lead has not been engaged recently.")
        next_actions.append("Send personalized follow-up within 24 hours.")

    if lead.get("status") in {"New", "Working"} and not lead.get("next_meeting"):
        risks.append("No next meeting is scheduled.")
        next_actions.append("Book qualification call and confirm agenda.")

    if lead.get("score", 0) < 50:
        risks.append("Lead score is below target threshold.")
        next_actions.append("Enrich lead profile before deeper outreach.")

    health = "green" if not risks else ("amber" if len(risks) == 1 else "red")
    status = {"green": "healthy", "amber": "attention", "red": "at_risk"}[health]

    while len(next_actions) < 3:
        next_actions.append(
            [
                "Confirm decision process and timeline.",
                "Align next step with owner and due date.",
                "Attach latest call notes in CRM.",
            ][len(next_actions)]
        )

    return {
        "entity": {"type": "lead", "id": lead.get("id"), "name": lead.get("name"), "email": lead.get("email")},
        "summary": f"Lead {lead.get('name')} is {status} with {len(risks)} open risk(s).",
        "status": status,
        "health": health,
        "open_risks": risks,
        "recent_activity": lead.get("recent_activities", [])[:5],
        "next_actions": next_actions[:3],
        "sources": lead.get("sources", []),
    }

