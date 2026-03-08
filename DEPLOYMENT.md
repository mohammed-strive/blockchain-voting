# DEPLOYMENT

This document elucidates the pre-requisites and deployment steps for deploying the voting service.

## Pre-Requisites

The following environment variables should be populated before the build.

- SEPOLIA_RPC_URL: This is the RPC URL for the blockchain.
- PRIVATE_KEY: Private key for cryptographically signing all the contracts.
- WALLET_ADDRESS: A valid wallet address with reserve cryptocurrency to enable transactions on the blockchain.

- Git
- Python 3.9+
- A valid Crypto wallet (MetaMask).
- Access to a valid block chain infrastructure to deploy the app (Alchemy, Infura).

## Setup Guide

1. Clone the repository `git clone https://github.com/your-username/decentralized-voting`.
2. Install the dependencies - `pip install -r requirements.txt`
3. Compile the Voting contract file - `python scripts/compile_contract.py`
4. Start the FastAPI server - `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`