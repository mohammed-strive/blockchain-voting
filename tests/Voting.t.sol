// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Voting.sol";

contract VotingTest is Test {
    Voting voting;

    address ownerAddr = address(this);
    address voter1 = address(0x1);
    address voter2 = address(0x2);
    address attacker = address(0x3);

    function setUp() public {
        voting = new Voting();
    }

    function testInitialState() public view {
        assertEq(voting.owner(), ownerAddr);
        assertEq(voting.proposalCount(), 0);
    }

    function testCreateProposalIncrementsCountAndStoresData() public {
        voting.createProposal("Title", "Desc");

        assertEq(voting.proposalCount(), 1);
        (uint256 id, string memory title, string memory desc, uint256 votes, address creator, bool active)
            = voting.proposals(1);

        assertEq(id, 1);
        assertEq(title, "Title");
        assertEq(desc, "Desc");
        assertEq(votes, 0);
        assertEq(creator, ownerAddr);
        assertTrue(active);
    }

    event ProposalCreated(uint256 indexed id, string title, address creator);

    function testVoteOncePerAddress() public {
        voting.createProposal("Title", "Desc");

        vm.prank(voter1);
        voting.vote(1);
        (, , , uint256 votes,,) = voting.proposals(1);
        assertEq(votes, 1);

        vm.prank(voter1);
        vm.expectRevert(bytes("Already voted on this proposal"));
        voting.vote(1);
    }

    function testVoteFailsForInactiveProposal() public {
        voting.createProposal("Title", "Desc");
        voting.deactivateProposal(1);

        vm.prank(voter1);
        vm.expectRevert(bytes("Proposal not active"));
        voting.vote(1);
    }

    function testVoteFailsForNonexistentProposal() public {
        vm.prank(voter1);
        vm.expectRevert(bytes("Invalid proposal ID"));
        voting.vote(999);
    }

    function testDeactivateProposalOnlyOwner() public {
        voting.createProposal("Title", "Desc");

        vm.prank(attacker);
        vm.expectRevert(bytes("Unauthorized: Only owner can perform this action"));
        voting.deactivateProposal(1);

        // owner can deactivate
        voting.deactivateProposal(1);
        (, , , , , bool active) = voting.proposals(1);
        assertFalse(active);
    }

    function testGetProposalMatchesStorage() public {
        voting.createProposal("Title", "Desc");

        Voting.Proposal memory p = voting.getProposal(1);
        assertEq(p.id, 1);
        assertEq(p.title, "Title");
        assertEq(p.description, "Desc");
        assertTrue(p.active);
    }

    function testGetAllProposalsReturnsAll() public {
        voting.createProposal("A", "a");
        voting.createProposal("B", "b");

        Voting.Proposal[] memory all = voting.getAllProposals();
        assertEq(all.length, 2);

        assertEq(all[0].id, 1);
        assertEq(all[0].title, "A");

        assertEq(all[1].id, 2);
        assertEq(all[1].title, "B");
    }
}
