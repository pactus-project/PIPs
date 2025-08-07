---
pip: 43
title: Split Rewards
description: Split Block Rewards
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
discussion-no:
created: 2025-08-07
---

## Abstract

This PIP proposes modifying the block reward distribution mechanism to split rewards between
Validators and the Pactus Foundation.

## Motivation

To enhance the sustainability and trust in the Pactus economy,
this proposal merges the existing "Foundation" and "Team & Operations" funds into the Treasury account and
modifies the block reward mechanism.
Moving forward, rewards will be split between Validators and the treasury, according to a fixed ratio:

- 70% to Validators
- 30% to the Pactus Foundation

## Specification

This proposal requires that [PIP-39](https://pips.pactus.org/PIPs/pip-39) — Batch Transfer — be adopted and enabled.
With Batch Transfer support, block rewards can be split automatically between
the Validator and the Foundation in a single transaction.

The new reward distribution will follow this ratio:

- **0.7** to the Validator (proposer of the block)
- **0.3** to the Foundation addresses.

Additionally, the balances of the existing Foundation and Team & Operations accounts will be merged into
the Treasury account as follows:

1. **Foundation Address:**
   `pc1z2r0fmu8sg2ffa0tgrr08gnefcxl2kq7wvquf8z`

   Balance: 8,400,000.194910010

2. **Team & Operations Address:**
   `pc1znn2qxsugfrt7j4608zvtnxf8dnz8skrxguyf45`

   Balance: 3,779,999.999010000

### Foundation Address

The Pactus Foundation addresses are defined as follows:

<TBD: 100 addresses>
Activation

This PIP will be activated at block height yyy.
The transactions that transfer the existing funds to the Foundation addresses will be committed at block height xxxx.
