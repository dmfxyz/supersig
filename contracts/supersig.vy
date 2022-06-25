
## Structs ##
struct Proposal:
    target: address
    calldata: Bytes[20000]

## Events ##
event Proposed:
    proposer: indexed(address)
    proposalId: indexed(uint256)

## State Variables ##
owners: public(DynArray[address, 69])
minimum: public(uint32)
myself: public(address)

## Map from proposal ID  
proposals: public(HashMap[uint256, Proposal])
approvals: public(HashMap[uint256, uint256])
approved: HashMap[uint256,DynArray[address, 69]]

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

@external
def approve(id: uint256):
    is_owner: bool = False
    for owner in self.owners:
        if owner == msg.sender:
            is_owner = True
            break
    if is_owner == False:
        raise "Only owners can approve proposals"
    
    self.approvals[id] = self.approvals[id] + 1
    