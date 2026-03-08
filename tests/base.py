import os
import unittest
from fastapi.testclient import TestClient
from backend.main import app


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SEPOLIA_RPC_URL"] = os.getenv("SEPOLIA_RPC_URL","http://localhost:8545")
        cls.client = TestClient(app)