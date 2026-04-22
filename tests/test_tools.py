import unittest

from mcp_server.server import get_account_360, get_lead_360, health_check, search_entities


class ToolTests(unittest.TestCase):
    def test_health_check(self) -> None:
        payload = health_check()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("db_path", payload)

    def test_search_entities_validation(self) -> None:
        payload = search_entities(query="Acme", entity_type="invalid")
        self.assertIn("error", payload)

    def test_get_account_360(self) -> None:
        payload = get_account_360(account_id="acc_001")
        self.assertEqual(payload["entity"]["id"], "acc_001")
        self.assertEqual(len(payload["next_actions"]), 3)

    def test_get_lead_360(self) -> None:
        payload = get_lead_360(lead_id="lead_001")
        self.assertEqual(payload["entity"]["id"], "lead_001")
        self.assertEqual(len(payload["next_actions"]), 3)


if __name__ == "__main__":
    unittest.main()

