import pytest
from ape import accounts, project
from ape.types import HexBytes

@pytest.fixture()
def supersig(accounts):
    deployer = accounts[0]
    return deployer.deploy(project.supersig, [accounts[0], accounts[1], accounts[2]], 3)


def test_init(supersig, accounts):
    assert supersig.minimum() == 3
    assert supersig.owners(0) == accounts[0]
    assert supersig.owners(1) == accounts[1]
    assert supersig.owners(2) == accounts[2]
    assert supersig == supersig.myself()

def test_proposal(supersig, accounts):
    target = "0x000000000000000000000000000000000000dead"
    calldata = "0xbeaf"
    supersig.propose(1, target, calldata, sender=accounts[0])
    assert supersig.proposals(1).target.lower() == target
    assert supersig.proposals(1).calldata == HexBytes(calldata)

def test_approval(supersig, accounts):
    target = "0x000000000000000000000000000000000000dead"
    calldata = "0xbeaf"
    supersig.propose(1, target, calldata, sender=accounts[0])
    supersig.approve(1, sender=accounts[0])
    assert supersig.approvals(1) == 1

def test_approval_bad_caller(supersig, accounts):
    target = "0x000000000000000000000000000000000000dead"
    calldata = "0xbeaf"
    supersig.propose(1, target, calldata, sender=accounts[0])
    supersig.approve(1, sender=accounts[0])
    with pytest.raises(Exception):
        supersig.approve(1, sender=accounts[4])