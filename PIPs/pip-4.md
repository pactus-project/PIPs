---
pip: 4
title: Indexing Public Keys
status: Final
type: Standards Track
discussion-no: 18
author: Kayhan Alizadeh <me@kehiy.net>
category: Core
created: 2023-08-27
---

## Abstract

This document proposes the removal of the PublicKey from transactions if it is already known.

## Motivation

Removing known public keys from transactions could reduce the size of the blockchain.

## Specification

To be able to reconstruct a transaction from the raw data, a new field named `Flags` will be added to the transaction.
The `Flags` field is one byte, and if the first bit of the `Flags` is set to `1`,
it indicates that the public key is known and excluded from the transaction.

Once a transaction is committed for the first time, its public key can be indexed by the associated address.
If the same signer broadcasts another transaction, the public key can be safely removed from the transaction
as it is already known and indexed by the signer's address.

### Transaction ID

The `Flags` field will be excluded from the hash data, and the hash computes only from the Header and Payload data.

![Indexed public key](../assets/pip-4/indexed-public-key.png)

## Security Considerations

The proposed change has security implications that need to be considered.

An adversary can change the value of the `Flags` in two ways:

1. If the public key is not indexed or unknown yet, they can change the first bit of the `Flags` to `1`.
   In this case, an honest node receiving this transaction cannot validate the transaction
   because it doesn't have the public key, and the transaction will be invalid.

2. If the public key is indexed or known before, they can change the first bit of the `Flags` to `0`.
   Because the `Flags` is set to `0`, it means the public key is included in the transaction.
   In this case, the public key is redundant data.
