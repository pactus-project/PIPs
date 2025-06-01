---
pip: 39
title: Batch Transfer
description: Transfer Payload with Multiple Receivers
author: Pactus Development Team <info@pactus.org>
status: Accepted
type: Standards Track
category: Core
discussion-no: 232
created: 2025-05-12
---

## Abstract

This proposal introduces support for a Batch Transfer payload, enabling a one-to-many scheme for transferring PAC.

## Motivation

Batch transfers enable users to include multiple recipients in a single transfer payload, known as `BatchTransfer`,
which is executed simultaneously.
This functionality is particularly advantageous for users who wish to send PACs to multiple accounts in one transaction.

## Specifications

Currently, transactions in Pactus can include the following payloads:

- Transfer Payload
- Bond Payload
- Unbond Payload
- Withdraw Payload
- Sortition Payload

This PIP proposes the addition of a new payload type: **Batch Transfer**.

The `BatchTransfer` payload will be structured as follows:

| Field               | Type      | Size     | Description                                |
| ------------------- | --------- | -------- | ------------------------------------------ |
| From                | `Address` | 21 Bytes | Sender's address                           |
| NumberOfRecipients  | `Number`  | Variant  | Number of recipients                       |
| Recipients[].To     | `Address` | 21 Bytes | Receiver's address (within each recipient) |
| Recipients[].Amount | `Amount`  | Variant  | Amount to transfer (within each recipient) |

The Batch Transfer payload will be encoded deterministically.
The number of recipients will be used to decode the recipients.

## Backwards Compatibility

Batch transfers are **not** backward-compatible.
This feature will be activated at block number `4,703,760` on the Mainnet.
Older versions of the software will not be able to decode or process Batch Transfers.

## Security Considerations

TThe payload will only execute if all recipient addresses are valid and
the total sum of the amounts does not exceed the sender’s available balance.
The number of recipients is capped at 8 to prevent excessively large transactions that could strain network resources.
