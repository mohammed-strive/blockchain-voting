from pydantic import BaseModel
from typing import Optional


class ProposalCreate(BaseModel):
    title: str
    description: str


class VoteRequest(BaseModel):
    proposal_id: int
    voter_address: Optional[str] = None


class ProposalResponse(BaseModel):
    id: int
    title: str
    description: str
    vote_count: int
    creator: str
    active: bool


class TransactionResponse(BaseModel):
    tx_hash: str
    proposal_id: Optional[int] = None
    block_number: int
    message: str
