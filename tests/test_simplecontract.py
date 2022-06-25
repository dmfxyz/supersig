import pytest
from ape import accounts, project

@pytest.fixture
def helloworld(accounts):
    deployer = accounts[0]
    print(deployer)
    return deployer.deploy(project.simple_contract)


def test_helloworld(helloworld, accounts):
    helloworld.say_hello(sender=accounts[0])
    assert helloworld.calls(accounts[0]) == 1