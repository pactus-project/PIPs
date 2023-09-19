---
pip: 9
title: Removing Stamp
description: Removing Stamp from Transactions
author: Amir Babazadeh (@amirvalhalla)
status: Draft
type: Standards
category: Core
created: 2023-09-19
requires: PIP-2
---

## Abstract

This document proposes simplifying transactions by removing the `Stamp` field.

## Specification

Currently, transactions in `Pactus` are stamped. "Stamping a transaction" refers to adding a piece of information from a previously committed block to the transaction's header. In `Pactus`, stamps are represented by the first 4 bytes of a block hash.

Stamping transactions serve two primary purposes:

1. It specifies the interval for the execution of transactions.
2. It protects the main fork from long-range attacks.

In this section, we argue that removing the stamp will not compromise security and will simultaneously offer a more streamlined transaction format.

### LockTime vs. Stamp

With the finalization of [PIP-2](https://pips.pactus.org/PIPs/pip-2), each transaction now includes the LockTime field. LockTime is mandatory and should be set to the block that the transaction can be committed. Now, LockTime can be used for the execution time. In this case, the need to set the stamp is no longer necessary, and users will tend to ignore it.

### Long-Range Attack

Although stamping transactions can help prevent long-range attacks, any long-range fork can be ignored and rejected by the community. Therefore, stamping transactions appear to be a redundant field in transaction data.

## Security Considerations

Removing the stamp should not impact the security of the blockchain.
