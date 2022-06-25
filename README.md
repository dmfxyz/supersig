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