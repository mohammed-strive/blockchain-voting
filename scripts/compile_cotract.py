import json
import os
from solcx import compile_standard, install_solc # type: ignore

install_solc("0.8.20")

with open("contracts/Voting.sol", "r") as f1:
    source = f1.read()

compiled = compile_standard( # type: ignore
    {
        "language": "Solidity",
        "sources": {
            "Voting.sol": {
                "content": source,
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        },
    },
    solc_version="0.8.20",
)

os.makedirs("build", exist_ok=True)

with open("build/Voting.json", "w") as f2:
    json.dump(compiled, f2, indent=2)

abi = compiled["contracts"]["Voting.sol"]["Voting"]["abi"] # type: ignore
bytecode = compiled["contracts"]["Voting.sol"]["Voting"]["evm"]["bytecode"]["object"] # type: ignore

with open("build/abi.json", "w") as f3:
    json.dump(abi, f3, indent=2)

print("Contract compiled successfully. ABI and bytecode saved in the build directory.")
print(f"ABI functions: {[item['name'] for item in abi if item['type'] == 'function']}") # type: ignore

