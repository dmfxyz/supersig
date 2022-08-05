import pytest


from ape.types import HexBytes
from eth_utils import keccak
from eth_abi import encode_abi as abi_encode


@pytest.fixture(scope="session")
def hash_proposal():
    def hash_proposal(target, calldata, value, nonce):
        return keccak(
            abi_encode(["address", "bytes", "uint256", "uint256"], [target, calldata, value, nonce])
        )

    return hash_proposal


@pytest.fixture(scope="session")
def owners(accounts):
    return accounts[:3]


@pytest.fixture(scope="session")
def threshold():
    return 3


@pytest.fixture(scope="session")
def deployer(accounts):
    return accounts[0]  # NOTE: Also Owner 1


@pytest.fixture(scope="session")
def not_owner(accounts):
    return accounts[4]


@pytest.fixture()
def supersig(deployer, owners, project, threshold):
    return deployer.deploy(project.supersig, owners, threshold)


@pytest.fixture()
def supersig_with_proposal(supersig, owners, hash_proposal):
    proposal_hash = hash_proposal(
        "0x000000000000000000000000000000000000dead", HexBytes("0xbeaf"), 0, 420
    )
    supersig.approve(proposal_hash, sender=owners[0])
    return supersig, proposal_hash


@pytest.fixture()
def test_target_contract(deployer, project):
    return deployer.deploy(project.test_contract)
