import pytest
from ape import accounts, project
from ape.types import HexBytes
from ape.exceptions import ContractLogicError
from eth_utils import keccak
from eth_abi import encode_abi as abi_encode

@pytest.fixture()
def supersig(accounts):
    deployer = accounts[0]
    return deployer.deploy(project.supersig, [accounts[0], accounts[1], accounts[2]], 3)

@pytest.fixture()
def supersig_with_proposal(supersig, accounts):
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    supersig.propose(1,proposal_hash, sender=accounts[0])
    return supersig

@pytest.fixture()
def test_target_contract(accounts):
    deployer = accounts[0]
    return deployer.deploy(project.test_contract)

def test_init(supersig, accounts):
    assert supersig.minimum() == 3
    assert supersig.owners(0) == accounts[0]
    assert supersig.owners(1) == accounts[1]
    assert supersig.owners(2) == accounts[2]

def test_proposal(supersig, accounts):
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    supersig.propose(1, proposal_hash, sender=accounts[0])
    assert supersig.proposals(1).hash == proposal_hash # sorry https://eips.ethereum.org/EIPS/eip-55

def test_approval(supersig_with_proposal, accounts):
    supersig_with_proposal.approve(1, sender=accounts[0])
    assert supersig_with_proposal.approvals(1) == 1

def test_execute(supersig, test_target_contract, accounts):
    ## "set_magic_number(69)" courtesy of cast :) 
    target = test_target_contract.address
    calldata = HexBytes("0x70a5aa210000000000000000000000000000000000000000000000000000000000000045")
    value = 0
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    supersig.propose(2, proposal_hash, sender=accounts[0])

    ## Approve three times
    supersig.approve(2, sender=accounts[0])
    supersig.approve(2, sender=accounts[1])
    supersig.approve(2, sender=accounts[2])

    ## Execute
    supersig.execute(2, target, calldata, value, sender=accounts[0])

    ## Check that the proposal was executed
    assert test_target_contract.magic_number() == 0x45

def test_revoke(supersig_with_proposal, accounts):
    supersig_with_proposal.approve(1, sender=accounts[0])
    assert supersig_with_proposal.approvals(1) == 1
    supersig_with_proposal.revoke(1, sender=accounts[0])
    assert supersig_with_proposal.approvals(1) == 0

    ## should be able to approve again
    supersig_with_proposal.approve(1, sender=accounts[0])

def test_withdraw(supersig, accounts):
    target = accounts[4].address
    calldata = HexBytes("0x0")
    value = 42
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    accounts[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.propose(3, proposal_hash, sender=accounts[0])
    supersig.approve(3, sender=accounts[0])
    supersig.approve(3, sender=accounts[1])
    supersig.approve(3, sender=accounts[2])

    prev_balance = accounts[4].balance
    supersig.execute(3, target, calldata, value, sender=accounts[0])
    assert accounts[4].balance == prev_balance + 42

def test_deploy_with_value(accounts):
    deployer = accounts[0]
    contract = deployer.deploy(project.supersig, [accounts[0], accounts[1], accounts[2]], 3, value=1)
    assert contract.balance == 1

def test_fail_propose_already_exists(supersig_with_proposal, accounts):
    with pytest.raises(ContractLogicError):
        supersig_with_proposal.propose(1, keccak(HexBytes("0x0")), sender=accounts[0])

def test_fail_approval_bad_caller(supersig_with_proposal, accounts):
    with pytest.raises(ContractLogicError):
        supersig_with_proposal.approve(1, sender=accounts[4])

def test_fail_approve_twice(supersig_with_proposal, accounts):
    ## approve once
    supersig_with_proposal.approve(1, sender=accounts[0])
    ## try to approve again
    with pytest.raises(ContractLogicError):
        supersig_with_proposal.approve(1, sender=accounts[0])

def test_fail_execute_too_few_approvals(supersig_with_proposal, accounts):
    ## approve once
    supersig_with_proposal.approve(1, sender=accounts[0])
    ## try to approve again
    try:
        target = "0x000000000000000000000000000000000000dead"
        calldata = HexBytes("0xbeaf")
        value = 0
        supersig_with_proposal.execute(1, target, calldata, value, sender=accounts[1])
        assert False
    except ContractLogicError as e:
        assert e.message == "Proposal has not been approved by the minimum number of owners"

def test_fail_execute_does_not_exist(supersig, accounts):
    try:
        supersig.execute(0, "0x000000000000000000000000000000000000dead", HexBytes("0x0"), 0, sender=accounts[0])
        assert False
    except ContractLogicError as e:
        assert e.message == "Proposal has not been approved by the minimum number of owners"
    

def test_fail_execute_twice(supersig, accounts):
    target = accounts[4].address
    calldata = HexBytes("0x0")
    value = 42
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    accounts[0].transfer(supersig, value=42)
    assert supersig.balance == 42
    supersig.propose(3, proposal_hash, sender=accounts[0])
    supersig.approve(3, sender=accounts[0])
    supersig.approve(3, sender=accounts[1])
    supersig.approve(3, sender=accounts[2])

    prev_balance = accounts[4].balance
    supersig.execute(3, target, calldata, value, sender=accounts[0])
    assert accounts[4].balance == prev_balance + 42
    prev_balance = accounts[4].balance

    ## try to execute again
    try:
        supersig.execute(3, target, calldata, value, sender=accounts[0])
        assert False
    except ContractLogicError as e:
        assert e.message == "Proposal has not been approved by the minimum number of owners"
        assert accounts[4].balance == prev_balance

def test_fail_revoke_no_approval(supersig, accounts):
    with pytest.raises(ContractLogicError):
        supersig.revoke(1, sender=accounts[0])


def test_fail_calldata_doesnt_match_hash(supersig, test_target_contract, accounts):
    ## "set_magic_number(69)" courtesy of cast :) 
    target = "0x000000000000000000000000000000000000dead"
    calldata = HexBytes("0xbeaf")
    value = 0
    proposal_hash = keccak(abi_encode(['address', 'bytes', 'uint256'], [target, calldata, value]))
    supersig.propose(2, proposal_hash, sender=accounts[0])

    ## Approve three times
    supersig.approve(2, sender=accounts[0])
    supersig.approve(2, sender=accounts[1])
    supersig.approve(2, sender=accounts[2])

    ## Execute
    try:
        supersig.execute(2, target, calldata, 420, sender=accounts[0])
    except ContractLogicError as e:
        assert e.message == "Proposal hash does not match provided data"
