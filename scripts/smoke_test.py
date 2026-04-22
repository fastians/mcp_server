from __future__ import annotations

import json

from mcp_server.server import get_account_360, get_lead_360, health_check, search_entities


def _print_step(title: str, payload: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2))


def run_smoke_test() -> None:
    _print_step("1) Health", health_check())
    _print_step("2) Search account", search_entities(query="Acme", entity_type="account"))
    _print_step("3) Account 360", get_account_360(account_id="acc_001"))
    _print_step("4) Lead 360", get_lead_360(lead_id="lead_001"))


if __name__ == "__main__":
    run_smoke_test()
