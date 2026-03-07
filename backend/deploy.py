import os
import json
from dotenv import load_dotenv
from web3 import Web3


load_dotenv()

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = os.getenv("WALLET_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "cannot connect to Sepolia RPC"

with open("build/abi.json", "r") as f:
    abi = json.load(f)

with open("build/Voting.sol", "r") as f:
    compiled = json.load(f)

bytecode = compiled["contracts"]["Voting.sol"]["evm"]["bytecode"]["object"]
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(ACCOUNT)
transaction = contract.constructor().build_transaction(
    {
        "from": ACCOUNT,
        "nonce": nonce,
        "gas": 3_000_000,
        "gasPrice": w3.eth.gas_price,
    }
)

signed = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Deploying -> transaction hash = {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

with open(".env", "a") as f:
    f.writelines([f"CONTRACT_ADDRESS={contract_address}"])
