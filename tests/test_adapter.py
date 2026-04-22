import unittest

from application.db import init_db, seed_db
from application.service import ApplicationError, get_account_360, search_entities


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        init_db()
        seed_db()

    def test_search_entities_account(self) -> None:
        results = search_entities(query="Acme", entity_type="account")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "acc_001")

    def test_get_account_360(self) -> None:
        account_360 = get_account_360("acc_001")
        self.assertEqual(account_360["entity"]["name"], "Acme Corp")
        self.assertTrue(account_360["sources"])

    def test_missing_account_raises(self) -> None:
        with self.assertRaises(ApplicationError):
            get_account_360("acc_missing")

    def test_search_entities_rejects_empty_query(self) -> None:
        with self.assertRaises(ApplicationError):
            search_entities(query="   ", entity_type="account")


if __name__ == "__main__":
    unittest.main()

