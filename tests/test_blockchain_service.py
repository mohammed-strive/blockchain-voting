import unittest
from unittest.mock import MagicMock, patch
from backend.blockchain import BlockChainService


class TestBlockchainService(unittest.TestCase):
    @patch("backend.blockchain.Web3")
    def test_init_uses_env_and_connects(self, mock_web3_cls):
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_web3_cls.HTTPProvider.return_value = "provider"
        mock_web3_cls.return_value = mock_w3

        svc = BlockChainService()

        mock_web3_cls.HTTPProvider.assert_called()
        mock_w3.is_connected.assert_called_once()
        self.assertTrue(hasattr(svc, "contract"))

    @patch("backend.blockchain.Web3")
    def test_create_proposal_builds_tx(self, mock_web3_cls):
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_web3_cls.return_value = mock_w3

        mock_contract = MagicMock()
        mock_func = MagicMock()
        mock_event = MagicMock()
        mock_receipt = MagicMock()

        mock_receipt.transactionHash.hex.return_value = "0xabc"
        mock_receipt.blockNumber = 123
        mock_event.process_receipt.return_value = [{"args": {"id": 1}}]

        mock_contract.functions.createProposal.return_value = mock_func
        mock_contract.events.ProposalCreated.return_value = mock_event

        mock_w3.eth.contract.return_value = mock_contract
        mock_w3.eth.get_transaction_count.return_value = 7
        mock_w3.eth.gas_price = 1
        mock_w3.eth.send_raw_transaction.return_value = b"\x12"
        mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt

        svc = BlockChainService()
        svc.w3 = mock_w3
        svc.contract = mock_contract
        svc.account = "0x123"
        svc.private_key = "0xkey"

        result = svc.create_proposal("Title", "Desc")

        self.assertEqual(result["proposal_id"], 1)
        self.assertEqual(result["tx_hash"], "0xabc")
        self.assertEqual(result["block_number"], 123)

    @patch("backend.blockchain.Web3")
    def test_get_proposal_maps_fields(self, mock_web3_cls):
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_web3_cls.return_value = mock_w3

        mock_contract = MagicMock()
        mock_contract.functions.getProposal.return_value.call.return_value = (
            1,
            "Title",
            "Desc",
            5,
            "0xcreator",
            True,
        )
        mock_w3.eth.contract.return_value = mock_contract

        svc = BlockChainService()
        svc.w3 = mock_w3
        svc.contract = mock_contract

        p = svc.get_proposal(1)
        self.assertEqual(p["id"], 1)
        self.assertEqual(p["title"], "Title")
        self.assertEqual(p["vote_count"], 5)
        self.assertTrue(p["active"])


if __name__ == "__main__":
    unittest.main()
