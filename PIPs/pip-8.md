---
pip: 8
title: Defining address type based on the address usage
status: Final
type: Standards Track
author: |
    Kayhan Alizadeh <kehiiiiya@gmail.com>,
    B00f (@b00f)
category: Core
created: 2023-09-17
---

## Abstract

This proposal suggests defining the address type based on their usage, not the cryptographic algorithm.
With this approach, addresses can communicate their intended usage.

![PIP-8 - address format](../assets/pip-8/pactus_address.png)

## Motivation

Addresses in Pactus are defined as `<Type> + <20 Data>`.
Currently, the type only indicates the cryptographic algorithm of the corresponding public key.
It is defined as `1` for the BLS signature schema.
However, there are some problems with this approach:

1. The address can be misused.
   For example, a user might use an account address as a validator address in a
   [Bond transaction](https://docs.pactus.org/protocol/transaction/bond/)
   (An issue regarding this problem is reported [here](https://github.com/pactus-project/pactus/issues/510)).

1. The address doesn't indicate its usage.
   This makes it challenging for both humans and machines to identify the purpose of each address,
   whether it belongs to an `Account` or `Validator`. This is particularly troublesome in applications like block explorers.

## Specification

We propose to define address types as follows:

```text
0: Treasury address
1: Validator address
2: BLS-Account address
```

For the treasury address, the data is a string of zeros in 21-byte length: `000000000000000000000000000000000000000000`.
In both `Validator address` and `BLS-Account address`, the data is the hash of the corresponding public key.

## Examples

 Examples of validator address:

- `pc1p97d72u2nqfwq3rv3kfuy0xaeuvkk6ye5cl2vyp`
- `pc1ppjedvfsd02x74j83ceu0kju37652u253z9cnh6`
- `pc1pnetupg0ewf2r0l8hx9052d3g4zf8dpzlf9qgps`

Examples of BLS-account address:

- `pc1zwqxz2wmz5upuvxzj3kpgfq3k2are4s3ctqxtxy`
- `pc1zhjk4pujm770elt30ud2d868czg9kth3e3nefnl`
- `pc1zzya8am0h0y0nu6msxz5j5pt9tsqsdvgzs5r89v`

Note that validator addresses start with `pc1p`, and BLS account addresses start with `pc1z`.

## Address derivation path

Currently, the wallet derivation path in Pactus is similar to [EIP-2334](https://eips.ethereum.org/EIPS/eip-2334).
To align with this proposal, we suggest changing the derivation path to:

```text
m / purpose' / coin_type' / address_type' / address_index
```

The apostrophe in the path indicates that hardened derivation is used.

Each level is defined as follows:

### Purpose

The purpose is set to `12381`, representing the BLS12-381 curve.
This indicates the use of the BLS subtree for the derivation path.

Hardened derivation is used at this level.

### Coin type

The coin type is set to `21888`, which matches the PAC coin type registered at
[SLIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md).

Hardened derivation is used at this level.

### Address type

The address type is same as the type of address, setting 1 for validators and 2 for accounts.
The value 0 is reserved and is not used.

Hardened derivation is used at this level.

### Address Index

Addresses start from index 0 and increase sequentially.
This number is similar to the child index in
[BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) derivation.

Non-Hardened derivation is used at this level.

## References

- [BIP-0044](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)
- [EIP-2334](https://eips.ethereum.org/EIPS/eip-2334)
