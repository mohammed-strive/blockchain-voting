// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Voting {
    struct Proposal {
        uint id;
        string title;
        string description;
        uint voteCount;
        address creator;
        bool active;
    }

    address public owner;
    uint public proposalCount;

    mapping(uint => Proposal) public proposals;
    mapping(uint => mapping(address => bool)) public hasVoted;

    event ProposalCreated(uint indexed id, string title, string description, address indexed creator);
    event CastVote(uint indexed proposalId, address indexed voter);

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized: Only owner can perform this action");
        _;
    }

    modifier proposalExists(uint _proposalId) {
        require(_proposalId > 0 && _proposalId <= proposalCount, "Invalid proposal ID");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function createProposal(string calldata _title, string calldata _description) external returns (uint) {
        proposalCount++;
        proposals[proposalCount] = Proposal({
            id: proposalCount,
            title: _title,
            description: _description,
            voteCount: 0,
            creator: msg.sender,
            active: true
        });
        emit ProposalCreated(proposalCount, _title, _description, msg.sender);
        return proposalCount;
    }

    function vote(uint _proposalId) external proposalExists(_proposalId) {
        require(proposals[_proposalId].active, "Proposal not active");
        require(!hasVoted[_proposalId][msg.sender], "Already voted on this proposal");

        hasVoted[_proposalId][msg.sender] = true;
        proposals[_proposalId].voteCount++;
        emit CastVote(_proposalId, msg.sender);
    }

    function deactivateProposal(uint _proposalId) external onlyOwner proposalExists(_proposalId) {
        proposals[_proposalId].active = false;
    }

    function getProposal(uint _proposalId) external view proposalExists(_proposalId) returns (Proposal memory) {
        return proposals[_proposalId];
    }

    function getAllProposals() external view returns (Proposal[] memory) {
        Proposal[] memory allProposals = new Proposal[](proposalCount);
        for (uint i = 1; i <= proposalCount; i++) {
            allProposals[i - 1] = proposals[i];
        }
        return allProposals;
    }
}