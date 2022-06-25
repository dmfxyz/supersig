

magic_number: public(uint256)

@external
def __init__():
    self.magic_number = 42

@external
def set_magic_number(num: uint256):
    self.magic_number = num