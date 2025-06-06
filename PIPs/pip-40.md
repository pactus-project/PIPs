---
pip: 40
title: Reallocation of Network Fees to Treasury
description: Redirect network fees from validators to the treasury account to sustain block rewards.
author: Javad Rajabzadeh (@ja7ad)
status: Draft
type: Standard
category: Core
discussion-no: 235
created: 2025-05-28
---

## Abstract

This proposal suggests redirecting all network fees (transaction, smart contract execution, etc.) from validators
to the treasury account.
This change will extend the sustainability of the Pactus treasury and ensure the continuity of validator block rewards
for future years.

## Motivation

The Pactus blockchain uses a staking model that enables even low-resource community members to participate as validators.
To incentivize participation, 1 coin is distributed from the treasury to a validator every 10 seconds for proposing a block,
amounting to 8640 coins per day. Additionally, validators currently receive all transaction fees, accelerating
depletion of the treasury.

With 42 million PAC initially allocated to the treasury, projections indicate the treasury will be exhausted in
approximately 13 years.
Without intervention, the network will no longer be able to distribute base block rewards after that point, threatening long-term
validator engagement and network security.

## Specification

- All network fees will be redirected from validators to the treasury account. These include:
   - Transaction processing fees
   - Smart contract execution fees
   - Other operation-related fees

- Validators will continue receiving 1 PAC per proposed block from the treasury account.

- No change to block time, staking rules, or validator selection logic.

- Treasury address: [000000000000000000000000000000000000000000](https://bootstrap1.pactus.org/account/address/000000000000000000000000000000000000000000)

## Backwards Compatibility

No backward compatibility issues found.

## Test Cases

- Simulate a block with:
   - 10 transactions, each paying a fee of 0.01 PAC
   - Current implementation: validator earns 1 PAC (base) + 0.1 PAC (fees)
   - Proposed implementation: validator earns only 1 PAC; treasury gains 0.1 PAC

- Validate:
   - Treasury balance increases by the sum of all fees
   - Validator balance increases only by the base reward

## Security Considerations

Redirecting fees to the treasury may slightly reduce short-term validator income but ensures long-term reward sustainability.
It may reduce incentive for spam transactions by removing fee revenue motivation. No additional attack vectors are introduced
by this proposal.
