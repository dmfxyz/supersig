
## TODO: 20000 is an arbitrary constant throughout

## Structs ##
struct Proposal:
    target: address
    calldata: Bytes[20000]

## Events ##
event Proposed:
    proposer: indexed(address)
    proposalId: indexed(uint256)

event Executed:
    executor: indexed(address)
    proposalId: indexed(uint256)

## State Variables ##
owners: public(DynArray[address, 69])
minimum: public(uint256)
myself: public(address)

## Map from proposal ID  
proposals: public(HashMap[uint256, Proposal])
approvals: public(HashMap[uint256, uint256])
approved: HashMap[uint256,DynArray[address, 69]]

@external
def __init__(_owners: DynArray[address, 69], _minimum: uint256):
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

    ## Check that someone can't approve twice
    previous_approvals: DynArray[address, 69] = self.approved[id]
    for approval in previous_approvals:
        if approval == msg.sender:
            raise "You have already approved this proposal"
    
    self.approvals[id] = self.approvals[id] + 1
    self.approved[id].append(msg.sender)

@external
def execute(id: uint256):
    ## Check that the proposal exists
    ## TODO: Figure out how to do a zero comparison for this in vyper
    # if self.proposals[id] == b'\x00':
    #     raise "Proposal does not exist"
    
    ## Check that the proposal has been approved by the minimum number of owners
    if self.approvals[id] < self.minimum:
        raise "Proposal has not been approved by the minimum number of owners"
    
    ## Execute the proposal
    ## TODO: Actually test that this return stuff works
    proposal: Proposal = self.proposals[id]
    ret: Bytes[20000] = raw_call(proposal.target, proposal.calldata, max_outsize=20000)
    log Executed(msg.sender, id)