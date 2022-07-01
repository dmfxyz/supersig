import ape
from ape.types import HexBytes
from eth_utils import keccak


def test_init(supersig, owners, threshold):
    assert supersig.minimum() == threshold
    for i, owner in enumerate(owners):
        assert supersig.owners(i) == owner


def test_approve(supersig, owners, hash_proposal):
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)
    supersig.approve(proposal_hash, sender=owners[0])
    assert supersig.proposals(proposal_hash).approvers[0] == owners[0]
    assert supersig.approvals(proposal_hash) == 1


def test_additional_approval(supersig_with_proposal, owners):
    supersig, proposal_hash = supersig_with_proposal
    supersig.approve(proposal_hash, sender=owners[1])
    assert supersig.approvals(proposal_hash) == 2
    assert supersig.proposals(proposal_hash).approvers[1] == owners[1]


def test_execute(supersig, test_target_contract, owners, hash_proposal):
    target = test_target_contract.address
    ## "set_magic_number(69)" courtesy of cast :)
    calldata = HexBytes(
        "0x70a5aa210000000000000000000000000000000000000000000000000000000000000045"
    )
    value = 0
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)
    supersig.approve(proposal_hash, sender=owners[0])

    ## Approve two more times
    supersig.approve(proposal_hash, sender=owners[1])
    supersig.approve(proposal_hash, sender=owners[2])

    ## Execute
    supersig.execute(target, calldata, value, nonce, sender=owners[0])

    ## Check that the proposal was executed
    assert test_target_contract.magic_number() == 0x45


def test_revoke(supersig_with_proposal, owners):
    supersig, proposal_hash = supersig_with_proposal
    # Fixture already has one approval by owner[0]
    supersig.revoke(proposal_hash, sender=owners[0])
    assert supersig.approvals(proposal_hash) == 0

    ## should be able to approve again
    supersig.approve(proposal_hash, sender=owners[0])
    assert supersig.approvals(proposal_hash) == 1


def test_send_value(supersig, owners, not_owner, hash_proposal):
    target = not_owner.address
    calldata = HexBytes("0x0")
    value = 42
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)
    owners[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.approve(proposal_hash, sender=owners[0])
    supersig.approve(proposal_hash, sender=owners[1])
    supersig.approve(proposal_hash, sender=owners[2])

    prev_balance = not_owner.balance
    supersig.execute(target, calldata, value, nonce, sender=owners[0])
    assert not_owner.balance == prev_balance + 42


def test_deploy_with_value(owners, project):
    deployer = owners[0]
    contract = deployer.deploy(
        project.supersig, [owners[0], owners[1], owners[2]], 3, value=1
    )
    assert contract.balance == 1

def test_fail_approval_bad_caller(supersig_with_proposal, not_owner):
    supersig, proposal_hash = supersig_with_proposal
    with ape.reverts("Only owners can approve proposals"):
        supersig.approve(proposal_hash, sender=not_owner)


def test_fail_approve_twice(supersig_with_proposal, owners):
    supersig, proposal_hash = supersig_with_proposal
    ## try to approve again (already approved once in fixture)
    with ape.reverts("You have already approved this proposal"):
        supersig.approve(proposal_hash, sender=owners[0])


def test_fail_execute_too_few_approvals(supersig, owners, hash_proposal):
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0x0")
    value = 0
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)
    supersig.approve(proposal_hash, sender=owners[0])
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(target, calldata, value, nonce, sender=owners[0])


def test_fail_execute_does_not_exist(supersig, owners):
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(
            "0x000000000000000000000000000000000000dead",
            HexBytes("0x0"),
            0,
            0,
            sender=owners[0],
        )


def test_fail_execute_twice(supersig, owners, not_owner, hash_proposal):
    target = not_owner.address
    calldata = HexBytes("0x0")
    value = 42
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)
    owners[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.approve(proposal_hash, sender=owners[0])
    supersig.approve(proposal_hash, sender=owners[1])
    supersig.approve(proposal_hash, sender=owners[2])

    prev_balance = not_owner.balance
    supersig.execute(target, calldata, value, nonce, sender=owners[0])
    assert not_owner.balance == prev_balance + 42
    prev_balance = not_owner.balance

    ## try to execute again
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(target, calldata, value, nonce, sender=owners[0])

    assert not_owner.balance == prev_balance


def test_fail_revoke_no_approval(supersig_with_proposal, owners):
    supersig, proposal_hash = supersig_with_proposal
    with ape.reverts("No approval to revoke"):
        supersig.revoke(proposal_hash, sender=owners[1])


def test_fail_calldata_doesnt_match_hash(supersig, owners, hash_proposal):
    ## "set_magic_number(69)" courtesy of cast :)
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    nonce = 1337
    proposal_hash = hash_proposal(target, calldata, value, nonce)

    ## Approve three times
    supersig.approve(proposal_hash, sender=owners[0])
    supersig.approve(proposal_hash, sender=owners[1])
    supersig.approve(proposal_hash, sender=owners[2])

    ## Execute
    with ape.reverts("Proposal has not been approved by the minimum number of owners"):
        supersig.execute(target, calldata, value, 1338, sender=owners[0])
