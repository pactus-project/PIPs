---
pip: 53
title: Supporting secp256k1 Curve
description: Add secp256k1 (ECDSA) support, including encoding, addresses, and HD derivation
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
created: 2026-05-12
---

## Abstract

This PIP proposes adding support for the secp256k1 elliptic curve and the
associated ECDSA signature scheme. It defines address and key encodings for
secp256k1 key pairs, a fixed-size signature format, and a hierarchical
deterministic (HD) derivation path.

## Motivation

secp256k1 is the most widely used elliptic curve in blockchain ecosystems.
Adding native secp256k1 support to Pactus enables broader wallet interoperability,
reduces conversion costs for existing key material, and supports applications
already built on the curve.

Using deterministic ECDSA nonces according to RFC 6979 also improves resilience
against poor randomness in key generation and signing implementations.

## Specification

This proposal follows the secp256k1 curve parameters defined in [SEC 2](https://www.secg.org/sec2-v2.pdf)
and uses ECDSA signatures for signing and verification.

It also defines address and key encoding rules for secp256k1 key pairs,
as well as an HD derivation path suitable for secp256k1 key generation.

### Encoding

#### Address Format

This proposal introduces address type `4` as a new account address subtype for
secp256k1 public keys.
This is distinct from existing address types used in Pactus.

The address payload is derived from the compressed secp256k1 public key:

```text
address_data = ripemd160(blake2b_256(public_key))
```

Addresses are encoded using Bech32m.

```text
address_string = bech32m(HRP="pc", TYPE="4", DATA="<address_data>")
```

secp256k1 addresses start with `pc1y...`.

#### Public Key

secp256k1 public keys are compressed to 33 bytes using the standard
`0x02`/`0x03` prefix notation.

Public keys are serialized with Bech32m using a dedicated HRP.

```text
public_key_string = bech32m(HRP="public", TYPE="4", DATA="<compressed_public_key>")
```

#### Private Key

secp256k1 private keys are 32-byte values in the range `[1, n-1]`, where `n`
is the curve order.

Private keys are serialized with Bech32m using a dedicated HRP.

```text
private_key_string = bech32m(HRP="SECRET", TYPE="4", DATA="<private_key_data>")
```

#### Signature Format

ECDSA signatures use the secp256k1 curve and follow these rules:

- Message digests use BLAKE2b (`blake2b_256`).
- Signature values are generated using deterministic nonce generation per RFC 6979.
- The signature is encoded as a fixed 64-byte sequence: `r || s`.
- The value `s` MUST be in the lower half of the curve order to ensure a
  unique canonical representation.

Verification follows the standard ECDSA verification algorithm over secp256k1.

### HD Wallet

#### Derivation Path

For hierarchical deterministic key generation, this proposal follows [SLIP-10](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
and allows a non-hardened address index for secp256k1.

```text
m / purpose' / coin_type' / address_type' / address_index
```

#### Purpose

The purpose is set to `44`, following [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki).

Hardened derivation is used at this level.

#### Coin Type

The coin type is set to `21888`, which matches the PAC coin type registered in
[SLIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md).

Hardened derivation is used at this level.

#### Address Type

The address type is set to `4` for secp256k1 account addresses.

Hardened derivation is used at this level.

#### Address Index

Addresses start at index `0` and increase sequentially.

Non-hardened derivation is used at this level to support public-key-only address generation.

##### Example Paths

```text
m/44'/21888'/4'/0   # first secp256k1 account/address
m/44'/21888'/4'/1   # second secp256k1 account/address
```

## Test Cases

### Encoding Test Cases

The following test vectors demonstrate the encoding and decoding of secp256k1 keys and addresses:

- **Private Key Data (hex)**: `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`
- **Public Key Data (compressed hex)**: `036d6caac248af96f6afa7f904f550253a0f3ef3f5aa2fe6838a95b216691468e2`
- **Address Data (hex)**: `042bc1db7e0797c45b918dc401093c9257c6012b4c`
- **Encoded Private Key**: `SECRET1YQQQSYQCYQ5RQWZQFPG9SCRGWPUGPZYSNZS23V9CCRYDPK8QARC0SPVXU8Z`
- **Encoded Public Key**: `public1yqdkke2kzfzheda405lusfa2sy5aq70hn7k4zle5r322my9nfz35wyfamrfs`
- **Encoded Address**: `pc1y90qakls8jlz9hyvdcsqsj0yj2lrqz26vqu7l0z`
- **Message (bytes)**: `pactus`
- **Message Digest (hex)**: `ea020ace5c968f755dfc1b5921e574191cd9ff438639badae8a69f667e0d5970`
- **Signature (hex)**: `c86779676d217b04979434e5bd37eddd02b671e9a54b48d3a812c7862dcb539631bb5e8459fec007608f50ea5661e0a5215aac976705404cb4f36ee623e63199`

### HD Wallet Test Cases

For hierarchical deterministic wallet test vectors,
refer to [SLIP-0010](https://github.com/satoshilabs/slips/blob/master/slip-0010.md).

## Implementations

- [Python Implementation (No HD Wallet)](https://github.com/pactus-project/python-sdk)
