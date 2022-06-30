## SPDX-License-Identifier: MIT

## Structs ##
struct Proposal:
    hash: bytes32


## Events ##
event Proposed:
    proposer: indexed(address)
    proposalId: indexed(uint256)

event Executed:
    executor: indexed(address)
    proposalId: indexed(uint256)


## State Variables ##
MAX_OWNERS: constant(uint256) = 69
owners: public(DynArray[address, MAX_OWNERS])
minimum: public(uint256)

## Map from proposal ID
proposals: public(HashMap[uint256, Proposal])
approvals: public(HashMap[uint256, uint256])
approved: HashMap[uint256, DynArray[address, MAX_OWNERS]]


@external
@payable
def __init__(owners: DynArray[address, MAX_OWNERS], minimum: uint256):
    self.owners = owners
    self.minimum = minimum


@external
def propose(id: uint256, hash: bytes32):
    assert self.proposals[id].hash == EMPTY_BYTES32, "Proposal already exists"

    self.proposals[id] = Proposal({hash: hash})
    log Proposed(msg.sender, id)


@external
def approve(id: uint256):
    assert msg.sender in self.owners, "Only owners can approve proposals"
    assert msg.sender not in self.approved[id], "You have already approved this proposal"

    self.approvals[id] += 1
    self.approved[id].append(msg.sender)


@external
def revoke(id: uint256):
    prior_approvals: DynArray[address, MAX_OWNERS] = self.approved[id]

    # NOTE: This could be made a lot better with `enumerate` or `DynArray.index(item)`
    for index in range(MAX_OWNERS):
        if prior_approvals[index] == msg.sender:
            prior_approvals[index] = ZERO_ADDRESS
            self.approved[id] = prior_approvals
            self.approvals[id] -= 1
            return

    raise "No approval to revoke"


@external
def execute(id: uint256, target: address, calldata: Bytes[2000], amount: uint256):
    # NOTE: Not necessary because the 3rd check also catches this condition
    assert self.proposals[id].hash != EMPTY_BYTES32, "Proposal does not exist"
    assert self.approvals[id] >= self.minimum, "Proposal has not been approved by the minimum number of owners"
    assert self.proposals[id].hash == keccak256(_abi_encode(target, calldata, amount)), "Proposal hash does not match provided data"

    ## Execute the proposal
    proposal: Proposal = self.proposals[id]

    ## Neutralize proposal before executing
    self.proposals[id].hash = EMPTY_BYTES32
    self.approvals[id] = 0
    self.approved[id] = []

    ## Execute
    raw_call(target, calldata, value=amount)
    log Executed(msg.sender, id)


@external
@payable
def __default__():
    # NOTE: Required to send Ether to this wallet
    pass
