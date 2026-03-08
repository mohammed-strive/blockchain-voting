import unittest
from tests.base import BaseTestCase


class TestProposalAPIAnvil(BaseTestCase):
    def test_health_endpoint_connected_to_anvil(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["connected"])
        self.assertIsInstance(data["latest_block"], int)

    def test_create_proposal_and_fetch_it(self):
        payload = {
            "title": "Local Anvil Proposal",
            "description": "Testing against local chain"
        }
        resp = self.client.post("/proposals", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("proposal_id", data)
        proposal_id = data["proposal_id"]

        resp_get = self.client.get(f"/proposals/{proposal_id}")
        self.assertEqual(resp_get.status_code, 200)
        p = resp_get.json()[0]
        self.assertEqual(p["title"], payload["title"])
        self.assertEqual(p["description"], payload["description"])
        self.assertEqual(p["vote_count"], 0)
        self.assertTrue(p["active"])


if __name__ == "__main__":
    unittest.main()