---
pip: 49
title: Validator Delegation
author:
status: Draft
type: Standards Track
category: Core
discussion-no:
created: 2026-03-08
---

## Abstract

This PIP proposes a validator delegation mechanism that allows a stake owner to authorize another party to
operate a validator on their behalf. In return, block rewards are split between the validator operator and
the stake owner based on a predefined share.

## Motivation

Currently, only the stake owner can run a validator. Some users may not have the technical capability or
infrastructure to operate validator nodes, while still wanting to participate in staking.

This proposal enables stake owners to delegate validator operations to an operator and receive a configurable portion of
rewards without running validator infrastructure themselves.

## Specification

This proposal introduces two explicit roles:

- **Stake Owner**: the account that owns the bonded stake.
- **Validator Operator**: the key/entity that runs validator duties.

### Validator structure

The Pactus validator data structure is extended with an optional delegation section.

```go
type validatorData struct {
  PublicKey           *bls.PublicKey
  Number              int32
  Stake               amount.Amount
  LastBondingHeight   uint32
  UnbondingHeight     uint32
  LastSortitionHeight uint32

  // Optional delegation fields.
  DelegateOwner  crypto.Address // Stake owner account address
  DelegateShare  int64          // Owner share in nano PAC (portion of 1.0 PAC block reward)
  DelegateExpiry int32          // Block height at which delegation expires
}
```

If delegation fields are absent, the validator is treated as non-delegated.

### Bond transaction

The bond transaction includes optional delegation fields. If provided, the resulting validator is considered delegated
and must satisfy all delegation validation rules (share bounds, expiry validity, and owner address presence).

### Unbond transaction

For delegated validators, only the stake owner can submit an unbond transaction.

### Withdraw transaction

Only the stake owner can receive principal stake in withdrawal transactions.

## Reward distribution

`DelegateShare` defines the stake owner's reward share and MUST be within `[0, 0.7 PAC]`,
represented in nano PAC (`10^8` units per PAC).

The total block reward remains `1.0 PAC` and is distributed as:

1. Protocol share: `0.3 PAC`
2. Validator operator share: `0.7 PAC - DelegateShare`
3. Stake owner share: `DelegateShare`

The three outputs MUST sum to exactly `1.0 PAC`.

## Backward compatibility

To activate this proposal, the protocol block version is increased to `3` once a majority of validators have upgraded.
