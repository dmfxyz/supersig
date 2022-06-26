## SuperSig
<img src="./assets/supersig_cover.png" alt="sign stuff" width="494" height="200"/>

Supersig is a multisig written in vyper. It's intended to be used in coordination with the [supersig frontend](https://github.com/relyt29/supersig-frontend)

At a high level, Supersig works like this:
1. You deploy `supersig` with a list of owners and a minimum number of approvals
2. Someone `propose`'s a proposal
    - a proposal is very simple. It consists of an id, which is a number, and a proposal hash.
    - a proposal hash is a 32 bytes. It should be the keccak256 of a target address, some calldata, and an ethereum value.
3. Owners call `approve` on a proposal ID
4. Someone `executes` the proposal, providing the matching target address, calldata, and eth value. The proposal only executes if the hash of the execution arguments matches the proposal hash.

The intent of Supersig is to keep all approval and proposal actions on-chain, without revealing the intent of the proposal until it's executed.

Supersig was written as part of the ETHNYC 2022 Hackathon. It uses Apeworx, Vyper, Pokt, and Privy who were among the awesome sponsors of the event.

### Setup
Recommend using [miniconda](https://docs.conda.io/en/latest/miniconda.html)

1. Create a new environment and activate
```sh
$> conda create --name supersig python==3.10.4
$> conda activate supersig
```

2. Install [apeworx](https://www.apeworx.io/)
```sh
$> (supersig) python -m pip install -U pip
$> (supersig) python -m pip install eth-ape
$> (supersig) ape plugins install vyper
```

3. Make sure stuff works
```sh
$> ape test
========================================== test session starts ===========================================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-0.13.1
rootdir: /Users/Dan/scontract/supersig
plugins: eth-ape-0.3.3, web3-5.29.2
collected 15 items                                                                                       

tests/test_supersig.py ...............                                                             [100%]

========================================== 15 passed in 19.94s ===========================================
```

## Deploying to Testnet
(assumes you have a wallet with some Testnet eth)
1. Import the wallet to ape and give it the `testnet`
```sh
$> (supersig) ape accounts import testnet
```

2. Create three signer addresses for testing
```sh
$> (supersig) ape accounts generate signer1
$> (supersig) ape accounts generate signer2
$> (supersig) ape accounts generate signer3
```

3. Run deploy job
```sh
$> (supersig) ape run scripts/deploy_testnet.py --network ethereum:rinkeby
```
