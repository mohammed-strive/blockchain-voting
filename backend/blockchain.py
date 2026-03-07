import json
import os
from dotenv import load_dotenv
from eth_typing import 
from web3 import Web3

load_dotenv()


class BlockChainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
        assert self.w3.is_connected(), "Failed to connect to the blockchain"

        self.account = os.getenv("WALLET_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))

        with open("build/abi.json", "r") as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(address=self.contract_address, abi=abi)

    def _send_transaction(self, func):
        """
        This function does the following:
            Build, sign and broadcast a state changing transaction
        """
        nounce = self.w3.eth.get_transaction_count(self.account)
        transaction = func.build_transaction(
            {
                "from": self.account,
                "nounce": nounce,
                "gas": 300_000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )
        signed = self.w3.eth.account.sign_transaction(transaction, self.private_key)
        t_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(t_hash)
        return receipt

    def create_proposal(self, title: str, description: str) -> dict:
        func = self.contract.functions.createProposal(title, description)
        receipt = self._send_transaction(func)

        # Try and get the new proposal Id
        logs = self.contract.events.ProposalCreated().process_receipt(receipt)
        proposal_id = logs[0]["args"]["id"] if logs else None

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "proposal_id": proposal_id,
            "block_numner": receipt.BlockNumber,
        }
    
    def vote(self, proposal_id: int) -> dict:
        func = self.contract.functions.vote(proposal_id)
        receipt = self._send_transaction(func)

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block_number": receipt.BlockNumber,
        }

    def get_proposal(self, proposal_id: int) -> dict:
        p = self.contract.functions.getProposal(proposal_id).call()
        return {
            "id": p[0],
            "title": p[1],
            "description": p[2],
            "vote_count": p[3],
            "creator": p[4],
            "active": p[5],
        }
    
    def get_all_proposals(self) -> list:
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
