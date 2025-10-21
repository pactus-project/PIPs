---
pip: 46
title: Supporting Ed25519 Curve
description: Add Ed25519 (EdDSA) support including encoding, addresses, and HD derivation
author: Pactus Development Team <info@pactus.org>
status: Draft
category: Core
discussion-no: 266
created: 2025-10-20
---

## Abstract

This PIP proposes adding support for the Edwards-curve Digital Signature Algorithm (EdDSA)
using the Ed25519 parameter set, targeting a 128-bit security level.

## Motivation

Ed25519 is a widely adopted signature scheme that offers strong security,
constant-time implementations, compact keys/signatures, and excellent performance across platforms.
It is also deterministic, the nonce is derived from the private key and message (via SHA-512),
which simplifies reproducibility and removes reliance on external randomness.

## Specification

We follow [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.txt) for signing and
verifying messages using the Ed25519 variant of EdDSA.

This document specifies encoding/decoding formats and hierarchical deterministic (HD) derivation.

### Address Format

Based on [PIP-8](https://pips.pactus.org/PIPs/pip-8) we define address type `3` for Ed25519 curve.
The address payload is the hash of the public key.

```text
address_data = ripemd160(blake2b_256(public_key))
```

We use [Bech32m](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)
to encode the address into a human-readable string.

```text
address_string = bech32m(HRP="pc", TYPE="3", DATA="<address_data>")
```

### Public Key

We define signature type `3` for Ed25519 key pairs.

The public key is 32 bytes in the standard Ed25519 compressed form:
it encodes the y-coordinate, and the most significant bit of the final octet encodes
the sign bit of the x-coordinate. See RFC 8032 for details.

Public keys are encoded with Bech32m using a distinct HRP.

```text
public_key_string = bech32m(HRP="public", TYPE="3", DATA="<compressed_public_key>")
```

### Private Key

The Ed25519 private key is a 32-byte seed. It is encoded with Bech32m using a distinct HRP.

```text
private_key_string = bech32m(HRP="SECRET", TYPE="3", DATA="<private_key_seed>")
```

### Derivation PATH

We follow [SLIP-10](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
for private key derivation from the master seed.
The derivation path is defined as:

```text
m / purpose' / coin_type' / address_type' / address_index'
```

### Purpose

The purpose is set to `44`, following [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki).

Hardened derivation is used at this level.

### Coin type

The coin type is set to `21888`, which matches the PAC coin type registered at
[SLIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md).

Hardened derivation is used at this level.

### Address type

The address type matches the address type. For Ed25519 we set it to `3`.

Hardened derivation is used at this level.

### Address Index

Addresses start from index 0 and increase sequentially.
This number is similar to the child index in
[BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) derivation.

Hardened derivation is used at this level.

Note: Ed25519-based derivation does not support non-hardened children. All path components MUST be hardened.

#### Example paths

```text
m/44'/21888'/3'/0'   # first Ed25519 account/address
m/44'/21888'/3'/1'   # second Ed25519 account/address
```
