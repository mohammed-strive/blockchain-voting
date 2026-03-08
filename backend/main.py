from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.blockchain import BlockChainService
from backend.schemas import ProposalCreate, ProposalResponse, TransactionResponse

app = FastAPI(
    title="Voting API - BlockChain",
    description="BlockChain voting using smart contract with Sepolia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = BlockChainService()


@app.get("/health")
def health():
    connected = blockchain.w3.is_connected()
    block = blockchain.w3.eth.block_number
    return {"connected": connected, "latest_block": block}


@app.post("/proposals", response_model=TransactionResponse)
def create_proposal(body: ProposalCreate):
    try:
        res = blockchain.create_proposal(body.title, body.description)
        return TransactionResponse(
            tx_hash=res["tx_hash"],
            proposal_id=res["proposal_id"],
            block_number=res["block_number"],
            message="Proposal create: Success",
        )
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/proposals/{proposal_id}", response_model=list[ProposalResponse])
def list_proposals():
    try:
        return blockchain.get_all_proposals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/proposals/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: int):
    try:
        return blockchain.get_proposal(proposal_id=proposal_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/proposals/{proposal_id}/vote", response_model=TransactionResponse)
def cast_vote(proposal_id: int):
    try:
        res = blockchain.vote(proposal_id=proposal_id)
        return TransactionResponse(
            tx_hash=res["tx_hash"],
            block_number=res["block_number"],
            message=f"Vote casted for Proposal: #{proposal_id}"
    )
    except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/proposals/{proposal_id}/results")
def get_results(proposal_id: int):
    try:
        proposal = blockchain.get_proposal(proposal_id=proposal_id)
        return {
            "proposal_id": proposal_id,
            "title": proposal["title"],
            "vote_count": proposal["vote_count"],
            "active": proposal["active"],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/voters/{address}/voted/{proposal_id}")
def check_has_voted(address: str, proposal_id: int):
    try:
        voted = blockchain.has_voted(proposal_id=proposal_id, address=address)
        return {
            "address": address,
            "proposal_id": proposal_id,
            "has_voted": voted
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))