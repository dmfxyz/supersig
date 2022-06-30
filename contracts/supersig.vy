## SPDX-License-Identifier: MIT

## Structs ##
struct Proposal:
    hash: bytes32
    approvers: DynArray[address, MAX_OWNERS]


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
## Map from proposalID to Proposal
proposals: public(HashMap[uint256, Proposal])


@external
@payable
def __init__(owners: DynArray[address, MAX_OWNERS], minimum: uint256):
    self.owners = owners
    self.minimum = minimum


@view
@external
def approvals(id: uint256) -> uint256:
    return len(self.proposals[id].approvers)


@external
def propose(id: uint256, hash: bytes32):
    assert self.proposals[id].hash == EMPTY_BYTES32, "Proposal already exists"

    self.proposals[id].hash = hash
    log Proposed(msg.sender, id)


@external
def approve(id: uint256):
    assert msg.sender in self.owners, "Only owners can approve proposals"
    assert msg.sender not in self.proposals[id].approvers, "You have already approved this proposal"

    self.proposals[id].approvers.append(msg.sender)


@external
def revoke(id: uint256):
    approvers: DynArray[address, MAX_OWNERS] = []

    # NOTE: This could be made better with set logic
    for approver in self.proposals[id].approvers:
        if approver != msg.sender:
            approvers.append(approver)

    assert len(approvers) < len(self.proposals[id].approvers), "No approval to revoke"
    self.proposals[id].approvers = approvers


@external
def execute(id: uint256, target: address, calldata: Bytes[2000], amount: uint256):
    # NOTE: Not necessary because the 3rd check also catches this condition
    assert self.proposals[id].hash != EMPTY_BYTES32, "Proposal does not exist"
    assert len(self.proposals[id].approvers) >= self.minimum, "Proposal has not been approved by the minimum number of owners"
    assert self.proposals[id].hash == keccak256(_abi_encode(target, calldata, amount)), "Proposal hash does not match provided data"

    ## Neutralize proposal before executing
    self.proposals[id] = empty(Proposal)

    ## Execute
    raw_call(target, calldata, value=amount)
    log Executed(msg.sender, id)


@external
@payable
def __default__():
    # NOTE: Required to send Ether to this wallet
    pass
