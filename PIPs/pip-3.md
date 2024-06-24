---
pip: 3
title: Removing sequence field from transactions
author: B00f (@b00f)
status: Final
type: Standards Track
discussion-no: 19
category: Core
created: 2023-08-23
---

## Abstract

This document proposes to remove the `Sequence` field from the transactions.

## Motivation

The `Sequence` in Pactus is similar to the `nonce` in Ethereum.
It stops replay attacks by increasing the sequence number in the sender's account when a transaction is confirmed.
If the same transaction is replayed, it can be detected and rejected.
However, the sequence field makes it hard to implement the scheduled transactions.

This document proposes to remove the sequence field from transactions without compromising security.

## Specification

To detect a replayed transaction, we can check if it has already been confirmed.
This involves looking up confirmed transactions and checking for any with the same ID or hash.
If a matching transaction is found, it means the transaction is replayed and should be rejected.

### Light client implementation

A light client does not need to store all transaction IDs to verify new transactions.
Since Pactus transactions have a limited lifespan[^1], the light client can avoid keeping all transaction records.
For instance, with the current consensus parameters,
storing the transactions for a single day is sufficient to detect replay attacks.

## References

[^1]: [PIP-2: Lock Time Transactions](https://pips.pactus.org/PIPs/pip-2#time-to-live-interval)
