
event Hello:
    words: String[32]

calls: public(HashMap[address, uint256])
@external
def say_hello():
    prev: uint256 = self.calls[msg.sender]
    self.calls[msg.sender] = prev + 1
