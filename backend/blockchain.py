# backend/blockchain.py
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv, find_dotenv
from web3 import Web3
from web3.exceptions import ContractLogicError  # important

load_dotenv(find_dotenv(), override=True)


class BlockChainService:
    def __init__(self) -> None:
        rpc_url = os.getenv("SEPOLIA_RPC_URL")
        if not rpc_url:
            raise RuntimeError("SEPOLIA_RPC_URL is not set in environment")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Failed to connect to RPC: {rpc_url}")

        # signer (backend wallet)
        self.private_key = os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise RuntimeError("PRIVATE_KEY is not set in environment")

        self.account = self.w3.eth.account.from_key(self.private_key).address

        # contract address – MUST be the one printed by your deploy script
        contract_address = os.getenv("CONTRACT_ADDRESS")
        if not contract_address:
            raise RuntimeError("CONTRACT_ADDRESS is not set in environment")

        self.contract_address = Web3.to_checksum_address(contract_address)

        # ABI from build output
        with open("build/abi.json") as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=abi,
        )

    def _send_transaction(self, func) -> Any:
        """Build, sign and send a state-changing tx, surfacing revert reasons."""
        nonce = self.w3.eth.get_transaction_count(self.account)
        tx = func.build_transaction(
            {
                "from": self.account,
                "nonce": nonce,
                "gas": 300_000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        signed = self.w3.eth.account.sign_transaction(tx, self.private_key)

        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except ContractLogicError as e:
            # This is triggered on Solidity revert (e.g. "Already voted on this proposal")
            raise e

        # If status == 0, there was a revert without a decoded reason
        if receipt.status == 0:
            # Optional: replay call to extract revert reason (advanced pattern)
            raise ContractLogicError("Transaction reverted")

        return receipt

    # ---------- public API ----------

    def create_proposal(self, title: str, description: str) -> Dict[str, Any]:
        func = self.contract.functions.createProposal(title, description)
        receipt = self._send_transaction(func)

        logs = self.contract.events.ProposalCreated().process_receipt(receipt)
        proposal_id = logs[0]["args"]["id"] if logs else None

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "proposal_id": proposal_id,
            "block_number": receipt.blockNumber,
        }

    def vote(self, proposal_id: int) -> Dict[str, Any]:
        func = self.contract.functions.vote(proposal_id)
        receipt = self._send_transaction(func)
        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.blockNumber,
        }

    def get_proposal(self, proposal_id: int) -> Dict[str, Any]:
        p = self.contract.functions.getProposal(proposal_id).call()
        return {
            "id": p[0],
            "title": p[1],
            "description": p[2],
            "vote_count": p[3],
            "creator": p[4],
            "active": p[5],
        }

    def get_all_proposals(self) -> list[Dict[str, Any]]:
        proposals = self.contract.functions.getAllProposals().call()
        return [
            {
                "id": p[0],
                "title": p[1],
                "description": p[2],
                "vote_count": p[3],
                "creator": p[4],
                "active": p[5],
            }
            for p in proposals
        ]

    def has_voted(self, proposal_id: int, address: str) -> bool:
        return self.contract.functions.hasVoted(
            proposal_id, Web3.to_checksum_address(address)
        ).call()
