## SuperSig

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
============================= test session starts =============================
platform darwin -- Python 3.10.4, pytest-7.1.2, pluggy-0.13.1
rootdir: /Users/Dan/scontract/supersig
plugins: eth-ape-0.3.3, web3-5.29.2
collected 2 items                                                             

tests/test_supersig.py ..                                               [100%]

============================== 2 passed in 2.46s ==============================
```

## Deploying to Ropsten
(assumes you have a wallet with some Ropsten eth)
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
$> (supersig) ape run scripts/deploy_testnet_and_test.py --network ethereum:ropsten
```
