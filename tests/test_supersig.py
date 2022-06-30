import ape
from ape.types import HexBytes
from eth_utils import keccak


def test_init(supersig, owners, threshold):
    assert supersig.minimum() == threshold
    for i, owner in enumerate(owners):
        assert supersig.owners(i) == owner


def test_proposal(supersig, owners, hash_proposal):
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    proposal_hash = hash_proposal(target, calldata, value)
    supersig.propose(1, proposal_hash, sender=owners[0])
    assert supersig.proposals(1).hash == proposal_hash


def test_approval(supersig_with_proposal, owners):
    supersig_with_proposal.approve(1, sender=owners[0])
    assert supersig_with_proposal.approvals(1) == 1


def test_execute(supersig, test_target_contract, owners, hash_proposal):
    ## "set_magic_number(69)" courtesy of cast :)
    target = test_target_contract.address
    calldata = HexBytes(
        "0x70a5aa210000000000000000000000000000000000000000000000000000000000000045"
    )
    value = 0
    proposal_hash = hash_proposal(target, calldata, value)
    supersig.propose(2, proposal_hash, sender=owners[0])

    ## Approve three times
    supersig.approve(2, sender=owners[0])
    supersig.approve(2, sender=owners[1])
    supersig.approve(2, sender=owners[2])

    ## Execute
    supersig.execute(2, target, calldata, value, sender=owners[0])

    ## Check that the proposal was executed
    assert test_target_contract.magic_number() == 0x45


def test_revoke(supersig_with_proposal, owners):
    supersig_with_proposal.approve(1, sender=owners[0])
    assert supersig_with_proposal.approvals(1) == 1
    supersig_with_proposal.revoke(1, sender=owners[0])
    assert supersig_with_proposal.approvals(1) == 0

    ## should be able to approve again
    supersig_with_proposal.approve(1, sender=owners[0])


def test_withdraw(supersig, owners, not_owner, hash_proposal):
    target = not_owner.address
    calldata = HexBytes("0x0")
    value = 42
    proposal_hash = hash_proposal(target, calldata, value)
    owners[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.propose(3, proposal_hash, sender=owners[0])
    supersig.approve(3, sender=owners[0])
    supersig.approve(3, sender=owners[1])
    supersig.approve(3, sender=owners[2])

    prev_balance = not_owner.balance
    supersig.execute(3, target, calldata, value, sender=owners[0])
    assert not_owner.balance == prev_balance + 42


def test_deploy_with_value(owners, project):
    deployer = owners[0]
    contract = deployer.deploy(
        project.supersig, [owners[0], owners[1], owners[2]], 3, value=1
    )
    assert contract.balance == 1


def test_fail_propose_already_exists(supersig_with_proposal, owners):
    with ape.reverts():
        supersig_with_proposal.propose(1, keccak(HexBytes("0x0")), sender=owners[0])


def test_fail_approval_bad_caller(supersig_with_proposal, not_owner):
    with ape.reverts():
        supersig_with_proposal.approve(1, sender=not_owner)


def test_fail_approve_twice(supersig_with_proposal, owners):
    ## approve once
    supersig_with_proposal.approve(1, sender=owners[0])
    ## try to approve again
    with ape.reverts():
        supersig_with_proposal.approve(1, sender=owners[0])


def test_fail_execute_too_few_approvals(supersig_with_proposal, owners):
    ## approve once
    supersig_with_proposal.approve(1, sender=owners[0])
    ## try to approve again
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig_with_proposal.execute(1, target, calldata, value, sender=owners[1])


def test_fail_execute_does_not_exist(supersig, owners):
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(
            0,
            "0x000000000000000000000000000000000000dead",
            HexBytes("0x0"),
            0,
            sender=owners[0],
        )


def test_fail_execute_twice(supersig, owners, not_owner, hash_proposal):
    target = not_owner.address
    calldata = HexBytes("0x0")
    value = 42
    proposal_hash = hash_proposal(target, calldata, value)
    owners[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.propose(3, proposal_hash, sender=owners[0])
    supersig.approve(3, sender=owners[0])
    supersig.approve(3, sender=owners[1])
    supersig.approve(3, sender=owners[2])

    prev_balance = not_owner.balance
    supersig.execute(3, target, calldata, value, sender=owners[0])
    assert not_owner.balance == prev_balance + 42
    prev_balance = not_owner.balance

    ## try to execute again
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(3, target, calldata, value, sender=owners[0])

    assert not_owner.balance == prev_balance


def test_fail_revoke_no_approval(supersig, owners):
    with ape.reverts():
        supersig.revoke(1, sender=owners[0])


def test_fail_calldata_doesnt_match_hash(supersig, owners, hash_proposal):
    ## "set_magic_number(69)" courtesy of cast :)
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    proposal_hash = hash_proposal(target, calldata, value)
    supersig.propose(2, proposal_hash, sender=owners[0])

    ## Approve three times
    supersig.approve(2, sender=owners[0])
    supersig.approve(2, sender=owners[1])
    supersig.approve(2, sender=owners[2])

    ## Execute
    with ape.reverts("Proposal hash does not match provided data"):
        supersig.execute(2, target, calldata, 420, sender=owners[0])
