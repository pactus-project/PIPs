---
pip: 3
title: Removing sequence field from transactions
author: Mostafa Sedaghat Joo (@b00f)
status: Accepted
type: Standards Track
created: 2023-08-23
---

## Abstract

This document propose to remove the `Sequence` field from the transactions.

## Motivation

The `Sequence` in Pactus is similar to the `nonce` in Ethereum.
It stops replay attacks by increasing the sequence number in the sender's account when a transaction is confirmed.
If the same transaction is replayed, it can be detected and rejected.
However, the sequence field makes it hard to implement the scheduled transactions.

This document proposes to remove the sequence field from transactions without compromising security.

## Specification

To detect a replayed transaction, we can check if it has been confirmed before.
This involves looking up confirmed transactions and checking for any with the same hash.
If a matching transaction is found, it means the transaction is replayed and can be rejected.

To ensure unique hashes for all transactions, relying solely on random stamp data is not enough.
According to the Birthday Paradox [^1], a 32-bit hash has a more than 50% chance of collision after 80,000 blocks.
A simple solution is to make the `LockTime` field mandatory for all transactions.
The `LockTime` value should match the block number referenced by the Stamp.

### Light client implementation

A light client doesn't need to store the entire blockchain history.
Since Pactus transactions have a limited lifespan, the light client can avoid keeping all transaction records.
For example, with the current consensus parameters, the number of transactions in a single day is sufficient to detect replay attacks.

## References

[^1]: [https://en.wikipedia.org/wiki/Birthday_attack](https://en.wikipedia.org/wiki/Birthday_attack)
