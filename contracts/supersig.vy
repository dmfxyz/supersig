## SPDX-License-Identifier: MIT

## Structs ##
struct Proposal:
    approvers: DynArray[address, MAX_OWNERS]


## Events ##
event Approved:
    approver: indexed(address)
    hash: indexed(bytes32)

event Executed:
    executor: indexed(address)
    hash: indexed(bytes32)

event Revoked:
    revoker: indexed(address)
    hash: indexed(bytes32)


## State Variables ##
MAX_OWNERS: constant(uint256) = 69
owners: public(DynArray[address, MAX_OWNERS])
minimum: public(uint256)
## Map from proposalID to Proposal
proposals: public(HashMap[bytes32, Proposal])


@external
@payable
def __init__(owners: DynArray[address, MAX_OWNERS], minimum: uint256):
    self.owners = owners
    self.minimum = minimum


@view
@external
def approvals(hash: bytes32) -> uint256:
    return len(self.proposals[hash].approvers)


@external
def approve(hash: bytes32):
    assert msg.sender in self.owners, "Only owners can approve proposals"
    assert msg.sender not in self.proposals[hash].approvers, "You have already approved this proposal"

    self.proposals[hash].approvers.append(msg.sender)
    log Approved(msg.sender, hash)


@external
def revoke(hash: bytes32):
    approvers: DynArray[address, MAX_OWNERS] = []

    # NOTE: This could be made better with set logic
    for approver in self.proposals[hash].approvers:
        if approver != msg.sender:
            approvers.append(approver)

    assert len(approvers) < len(self.proposals[hash].approvers), "No approval to revoke"
    self.proposals[hash].approvers = approvers
    log Revoked(msg.sender, hash)


@external
def execute(target: address, calldata: Bytes[2000], amount: uint256, nonce: uint256):
    id: bytes32 =  keccak256(_abi_encode(target, calldata, amount, nonce))
    assert len(self.proposals[id].approvers) >= self.minimum, "Proposal has not been approved by the minimum number of owners"

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
