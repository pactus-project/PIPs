---
pip: 37
title: Batch Transaction
description: Transitions with multiple Payloads
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
discussion-no:
created: 2025-01-13
---

## Abstract

This proposal introduces support for batch transactions, enabling a single transaction to contain multiple payloads that are executed together.

## Motivation

Batch transactions enable users to include multiple payloads in a single transaction, executed simultaneously. This functionality is particularly advantageous for merchants receiving payments across multiple accounts or node operators bonding multiple validators in a single operation.

## Specifications

To designate that a transaction contains multiple payloads, a new flag, `0x2`, is introduced.
If this flag is not set, the transaction format remains unchanged.
When the flag is set, the transaction format is updated as follows:

| Field              | Size     |
| ------------------ | -------- |
| Flags              | 1 byte   |
| Version            | 1 byte   |
| Lock Time          | 4 bytes  |
| Fee                | Variant  |
| Memo               | Variant  |
| Number of Payloads | 1 byte   |
| Payload.Type     | 1 byte   |
| Payload.Data     | Variant  |
| Signature          | 48 bytes |
| Public Key         | 96 bytes |

To validate the transaction signature, all payloads must share the same signer address.

This format ensures that multiple payloads can be encoded and decoded without
altering the existing transaction structure.

## Backwards Compatibility

Batch transactions are not backward-compatible.
This feature should only be enabled once the majority of the network supports it.

## Security Considerations

There are several security considerations for batch transactions:

1. **Payload Limit**:
   The number of payloads is restricted to a maximum of 32 to prevent excessively large transactions.
2. **Atomic Execution**:
   Transactions with multiple payloads must be atomic.
   If one payload fails, none of the others should execute.
