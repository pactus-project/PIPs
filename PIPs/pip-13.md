---
pip: 13
title: Import Private Keys
description: Import private keys to wallet
author: Amir Babazadeh (@amirvalhalla)
status: Final
type: Standards Track
category: Core
created: 2023-11-27
---

## Abstract

Currently, the Pactus wallet does not support importing private keys.
This document proposes a method to import private keys.

## Motivation

Importing private keys will give users the ability to store external private keys inside the wallet safely.

## Specification

We propose adding a new Purpose [^1] for imported private keys and setting it to 65535 (FFFF).
The address path for imported private key is defined like below:

```text
m / purpose' / coin_type' / address_type' / import_index'
```

The apostrophe in the path indicates that hardened derivation is used.
For the imported private key all level are hardened and defined as follows:

- Purpose: Set to 65535 (0xFFFF).
- Coin Type: As defined at PIP-8[^2].
- Address Type: As defined at PIP-8[^2].
- Import Index: This is a fixed and hardened number that starts at zero.
  It indicates the position of a key in the list of imported keys. When new private keys are added,
  they are placed at the end of this list. This list must be securely encrypted using the wallet's password.

This structure is particularly useful for determining if an address is imported, based on the address path.
It also helps to sort the addresses better.

## Example

```text
m/65535'/21888'/1'/0'  // imported Validator address at index zero
m/65535'/21888'/2'/0'  // imported BLS-Account address at index zero
```

## References

[^1]: [BIP-0043: Purpose Field for Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0043.mediawiki)

[^2]: [PIP-8: Defining address type based on the address usage](https://pips.pactus.org/PIPs/pip-8)
