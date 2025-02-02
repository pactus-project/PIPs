---
pip: 37
title: Batch Transaction
description: Transitions with multiple Payloads
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
discussion-no: 213
created: 2025-01-13
---

## Abstract

This proposal introduces support for batch transactions,
enabling a single transaction to contain multiple payloads that are executed together.

## Motivation

Batch transactions enable users to include multiple payloads in a single transaction, executed simultaneously.
This functionality is particularly advantageous for merchants receiving payments across multiple accounts or
node operators bonding multiple validators in a single operation.

## Specifications

To designate that a transaction contains multiple payloads, a new flag, `0x2`, is introduced.
If this flag is not set, the transaction format remains unchanged.
When the flag is set, the transaction format is updated as follows:

| Field              | Size    |
| ------------------ | ------- |
| Flags              | 1 byte  |
| Version            | 1 byte  |
| Lock Time          | 4 bytes |
| Fee                | Variant |
| Memo               | Variant |
| Number of Payloads | 1 byte  |
| Payload.Type       | 1 byte  |
| Payload.Data       | Variant |
| Signature          | Variant |
| Public Key         | Variant |

To validate the transaction signature, all payloads must share the same signer address.

This format ensures that multiple payloads can be encoded and decoded without
altering the existing structure for single-payload transactions.
Transactions using the old format remain valid,
while the new format can be extended to support batch transactions.

#### Upgrade Version To 0x02:

The introduction of batch transactions necessitates a version upgrade from `0x01` to `0x02`.

1. **Batch Transaction Support:**
   - Transactions can now include multiple payloads, requiring an additional "Number of Payloads" field.
2. **New Transaction Flag (`0x2`)**:
   - This flag designates whether a transaction follows the new batch format.
   - If unset, transactions remain in the legacy format (`0x01`).
3. **Signature Validation Update:**
   - All payloads within a batch transaction must be signed by the same key.
4. **Backward Compatibility Handling:**
   - Nodes must support both `0x01` and `0x02` transaction formats during the upgrade transition.
   - Transactions in the old format (`0x01`) remain valid and are processed normally.
   - Nodes should reject batch transactions (`0x02`) if the network majority does not support them.
5. **Atomic Execution Requirement:**
   - If any payload in a batch transaction fails, all payloads are reverted to maintain consistency.

The upgrade from `0x01` to `0x02` ensures that the network can adopt batch transactions seamlessly
while preserving compatibility with existing transactions.

## Backwards Compatibility

Batch transactions are not backward-compatible.
The old format does not include the "Number of Payloads" field.
This feature should only be enabled once the majority of the network supports it.

## Security Considerations

There are several security considerations for batch transactions:

1. **Payload Limit**:
    The number of payloads is capped at 32 to prevent excessively large transactions that
    could strain network resources.
2. **Atomic Execution**:
   Transactions with multiple payloads must be atomic.
   If one payload fails, none of the others should execute.
