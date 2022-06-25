

owners: public(DynArray[address, 69])
minimum: public(uint32)
myself: public(address)

struct Proposal:
    target: address
    calldata: Bytes[20000]

## Map from proposal ID  
proposals: public(HashMap[uint256, Proposal])
approvals: public(HashMap[uint256, uint256])
approved: HashMap[uint256,DynArray[address, 69]]

event Proposed:
    proposer: indexed(address)
    proposalId: indexed(uint256)

@external
def __init__(_owners: DynArray[address, 69], _minimum: uint32):
    self.owners = _owners
    self.minimum = _minimum
    self.myself = self

@external
def propose(id: uint256, target: address, calldata: Bytes[20000]):
    ## TODO: Figure out how to do a zero comparison for this in vyper
    # if self.proposals[id] != b'\x00':
    #     raise "Proposal already exists"

    self.proposals[id] = Proposal({target: target, calldata: calldata})
    log Proposed(msg.sender, id)