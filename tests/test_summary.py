import unittest

from application.summary import compose_account_360, compose_lead_360


class SummaryTests(unittest.TestCase):
    def test_compose_account_360_shape(self) -> None:
        payload = compose_account_360(
            {
                "id": "acc_001",
                "name": "Acme Corp",
                "open_opportunities": [],
                "recent_activities": [],
                "sources": [{"record_type": "account", "record_id": "acc_001"}],
            }
        )
        self.assertEqual(payload["entity"]["type"], "account")
        self.assertIn("health", payload)
        self.assertIn("open_risks", payload)
        self.assertIn("next_actions", payload)
        self.assertEqual(len(payload["next_actions"]), 3)

    def test_compose_lead_360_shape(self) -> None:
        payload = compose_lead_360(
            {
                "id": "lead_001",
                "name": "Priya Sharma",
                "email": "priya@acme.com",
                "status": "Working",
                "score": 35,
                "last_activity_date": "2026-04-01",
                "next_meeting": None,
                "recent_activities": [],
                "sources": [{"record_type": "lead", "record_id": "lead_001"}],
            }
        )
        self.assertEqual(payload["entity"]["type"], "lead")
        self.assertIn(payload["health"], {"green", "amber", "red"})
        self.assertGreaterEqual(len(payload["open_risks"]), 1)
        self.assertEqual(len(payload["next_actions"]), 3)


if __name__ == "__main__":
    unittest.main()

