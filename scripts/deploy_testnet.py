from ape import accounts, project

def deploy():
    deployer = accounts.load("testnet")
    signer1, signer2, signer3 = accounts.load('signer1').address, accounts.load('signer2').address, accounts.load('signer3').address
    return deployer.deploy(project.supersig, [signer1, signer2, signer3], 3)

def main():
    deploy()