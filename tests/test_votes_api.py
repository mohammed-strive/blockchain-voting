import unittest
from tests.base import BaseTestCase

class TestVoteAPIAnvil(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        payload = {
            "title": "Anvil Voting Target",
            "description": "Proposal for voting tests"
        }
        resp = cls.client.post("/proposals", json=payload)
        assert resp.status_code == 200, resp.text
        cls.proposal_id = resp.json()["proposal_id"]

    def test_vote_once_increments_count(self):
        resp = self.client.post(f"/proposals/{self.proposal_id}/vote")
        self.assertEqual(resp.status_code, 200)

        res = self.client.get(f"/proposals/{self.proposal_id}/results")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["vote_count"], 1)

    def test_double_vote_fails(self):
        self.client.post(f"/proposals/{self.proposal_id}/vote")

        resp = self.client.post(f"/proposals/{self.proposal_id}/vote")
        self.assertEqual(resp.status_code, 200)

    def test_vote_on_nonexistent_proposal(self):
        resp = self.client.post("/proposals/9999999/vote")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()