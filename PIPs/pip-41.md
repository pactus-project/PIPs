---
pip: 41
title: Address Recovery
description: Recovering Addresses after Wallet Recovery
author: Pactus Development Team <info@pactus.org>
status: Accepted
type: Standards Track
category: Core
discussion-no: 242
created: 2025-03-22
---

## Abstract

This proposal enables automatic recovery of used addresses when restoring a wallet from a mnemonic phrase.

## Motivation

### Problem

Right now, when a wallet is recovered using a mnemonic phrase,
it cannot automatically restore all previously used or balance-holding addresses.
Users must manually create addresses, which is not efficient.
This can also cause problems, especially if there is a gap in address usage.

### Solution

This proposal suggests recovering addresses that have activity on the blockchain.
An address is considered active if its public key is stored in the blockchain database.
Otherwise, it is inactive or empty.

## Specification

When recovering a wallet from an external source (e.g., mnemonic phrase), the software should follow these steps:

1. Set `recovered_count = 1`.
2. Set `inactive_count = 1`.
3. Derive the first address.
4. Loop:
   * Check if the address's public key is indexed in the blockchain.
   * If **indexed** (active):
      * Add `inactive_count` to `recovered_count`.
      * Reset `inactive_count = 1`.
   * If **not indexed** (inactive):
      * Increase `inactive_count` by 1.
      * If `inactive_count > 8`, break the loop.
   * Derive the next address.

After finding all recoverable addresses,
the software should recover all addresses up to the total number of recovered addresses.

### Limitation

Users cannot **automatically** recover a used address if it is separated by more than 8 inactive or empty addresses.
In this case, the user needs to manually create addresses until they reach the desired one.

## Backward Compatibility

This change is backward-compatible.
