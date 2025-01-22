---
pip: 29
title:  Batch Transactions
author: Maximiliano Paz (@maxipaz)
discussion-no: 168
status: Deferred
type: Informational
category: Core
created: 05-08-2024
---

## Abstract

This document suggests supporting batch transactions. A batch transaction is a transaction that executes multiple
payloads and/or includes multiple receivers. This scheme is also known as One-To-Many transactions.

## Motivation

Batch Transactions enable users to send multiple transactions in one operation, potentially saving time and resources.
This is particularly useful for merchants who want to receive payments for their services in different accounts.
To support these businesses, we need to allow multiple receivers in a single transaction.

### Possible Usages

- **Mass Payments:** Sending payments to multiple employees or participants.
- **Staking Operations:** Bonding or unbonding tokens to/from multiple validators.
- **Airdrops:** Distributing tokens to a large number of users.
- **Dividends:** Paying out dividends to multiple stakeholders.
- **Donations:** Sending funds to multiple charitable organizations.
- **Rewards Distribution:** Allocating rewards to participants in a loyalty program.

## Specification

**Transaction Format:**

- Utilize the `Flags` field to indicate a Batch Transaction with a new flag: `0x02`.
- Modify Transfer Transactions to allow an array of receivers.
- Support different transaction types in one batch by using the `Payload Data` field
  (we should have an array of Payload Data).

### Pros

- **Efficiency:** Reduces the number of individual transactions processed.
- **Convenience:** Users can manage multiple transactions in one step.
- **Scalability:** Improves network throughput by bundling transactions.
- **Reduced Network Load:** Lowers the number of individual operations, potentially enhancing network performance.
- **Enhanced User Experience:** Simplifies the process for users with complex transaction needs.

### Cons

- **Complexity:** Increases the complexity of transaction validation and processing.
- **Security:** Requires rigorous security measures to prevent batch transaction abuse.
- **Redundancy:** If gas-less transactions are implemented, the primary benefit of batch transactions (cost saving) is diminished.
- **Debugging Difficulties:** Troubleshooting failed transactions can become more complex.
