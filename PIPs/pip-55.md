---
pip: 55
title: Block Reward Halving
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
created: 2026-06-24
---

## Abstract

This PIP proposes a block reward halving schedule for Pactus.
The reward starts at 1 PAC per block and undergoes three halvings with
doubling intervals: first at block 8,000,000, second at block 24,000,000,
and third at block 56,000,000.
After the third halving, the reward remains at 0.125 PAC per block.

## Motivation

Pactus currently issues a fixed reward of 1 PAC per block with no reduction over time.
This creates an unbounded linear supply with no long-term issuance discipline.

Reducing the reward over time serves two purposes:

1. **It limits supply.** A predictable issuance curve sets a natural supply trajectory
   rather than allowing indefinite dilution.

2. **It gives the network time to adapt.** Validators have years to adjust
   before each reduction. Transaction fees have time to grow and provide
   a larger share of validator income. The ecosystem has more time
   for integration and expansion before subsidies taper off.

## Specification

The reward is based on block height. The Foundation share is always 30%
of the block reward (per PIP-43).

| Start block | End block  | Reward per block | Total Blocks | Total PAC |
| ----------- | ---------- | ---------------- | ------------ | --------- |
| 1           | 8,000,000  | 1.000 PAC        | 8,000,000    | 8,000,000 |
| 8,000,001   | 24,000,000 | 0.500 PAC        | 16,000,000   | 8,000,000 |
| 24,000,001  | 56,000,000 | 0.250 PAC        | 32,000,000   | 8,000,000 |
| 56,000,001  | —          | 0.125 PAC        | —            | —         |

## Backward Compatibility

This change requires a protocol upgrade to version 4 via the mechanism
described in [PIP-51](https://pips.pactus.org/PIPs/pip-51).
Once more than 75% of the committee's power supports version 4,
the proposer increases the block version and the new reward schedule activates.
Nodes that do not upgrade will be unable to validate new blocks.

## Security Considerations

The halving boundaries are evaluated consistently across all nodes.
The reward amount at each boundary must match the values defined in this
specification exactly, and the schedule is deterministic — it must produce
identical results in every node implementation.
