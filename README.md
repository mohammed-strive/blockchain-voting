# Introduction

Blockchain-Voting app is a sample application to demonstrate the use of blockchain and smart contracts to build a solid, secure voting system. Some of the salient features of this sample application include

- Proposal creation
- Voting on a proposal
- Verifying proposals and votes on the blockchain
- Using smart contracts to ensure a distributed and secure ledger.

The application uses Solidity for creating the core blockchain contract and python for deploying the contract and creating a api service to interact with the deployed contract.

The application has the following parts

- A [Voting.sol](./contracts/Voting.sol) file which contains the core smart contract.
- [deploy.py](./backend/deploy.py) script to deploy the contract a blockchain infra.
- [main.py](./backend/main.py) service file which uses FastAPI to expose a set of routes to interact with the deployed contract.
- [compile_contract.py](./scripts/compile_cotract.py) A script to compile the contract and generate the ABI and a json contract file.

Setup and deployment is elucidated in [DEPLOYMENT.md](DEPLOYMENT.md)

## Tests

Tests for the service are in the [tests](./tests/) directory.

Run the tests from the root folder - `python -m unittest discover -s tests`

To run the solidity test for the contract file, you'll the need `forge` toolset. Run `forge test` inside the [voting-foundry](./voting-foundry/)