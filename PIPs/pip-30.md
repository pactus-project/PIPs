---
pip: 30
title: Fee Types
author: Pactus Development Team <info@pactus.org>
discussion-no: 171
status: Rejected
type: Informational
category: Core
created: 08-08-2024
---

## Abstract

This document introduces two types of transaction fees in the blockchain:

- Validator Fee
- Network Fee

Each transaction must pay these fees to be processed on the blockchain.

## Specification

The fee for a transaction is the sum of the validator fee and the network fee:

$$
\text{fee} = \text{validator_fee} + \text{network_fee}
$$

Both the validator fee and network fee can be zero.

### Validator Fee

The Validator Fee is the amount that block proposer can earn from the transactions.
These fees are determined by each validator individually and can be adjusted based on the validator's preferences.
Validators receive this fee as a reward, and the amount is credited to their reward address.
Validators can remove transactions with lower fees from the transaction pool.

### Network Fee

The Network Fee is the amount that each transaction must pay to be executed on the Pactus blockchain.
This fee is fixed within the network, and the amount is deposited into the treasury account.
This system is designed to recirculate fees back into the treasury,
which will eventually be evenly distributed among all validators.
