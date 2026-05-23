---
pip: 52
title: Supporting Ed25519 Curve
description: Add Ed25519 (EdDSA) support, including encoding, addresses, and HD derivation
author: Pactus Development Team <info@pactus.org>
status: Final
type: Standards Track
category: Core
created: 2026-05-12
---

## Abstract

This PIP proposes adding support for the Edwards-curve Digital Signature Algorithm (EdDSA)
using the Ed25519 parameter set, including new address and key encodings,
public/private key serialization, and hierarchical deterministic (HD) derivation.

## Motivation

Ed25519 is a widely adopted signature scheme that offers strong security,
constant-time implementations, compact keys and signatures, and excellent performance across platforms.
It is also deterministic: the nonce is derived from the private key and message (via SHA-512),
which removes reliance on external randomness and simplifies implementation.

## Specification

This proposal follows [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.txt)
for Ed25519 signing and verification.

It also defines address and encoding rules for Ed25519 key pairs,
as well as an HD derivation path suitable for Ed25519 key generation.

### Encoding

#### Address Format

This proposal introduces address type `3` as a new account address subtype for Ed25519 signatures.
This is distinct from existing address types used in Pactus.

The address payload is derived from the compressed Ed25519 public key:

```text
address_data = ripemd160(blake2b_256(public_key))
```

Addresses are encoded using Bech32m.

```text
address_string = bech32m(HRP="pc", TYPE="3", DATA="<address_data>")
```

Ed25519 addresses start with `pc1r...`.

#### Public Key

Ed25519 public keys are 32 bytes in their standard compressed form.
The compressed format encodes the y-coordinate, while the most significant bit of
the final octet encodes the sign of the x-coordinate, as defined in RFC 8032 (Section 5.1.5).

Public keys are serialized using Bech32m with a dedicated HRP.

```text
public_key_string = bech32m(HRP="public", TYPE="3", DATA="<compressed_public_key>")
```

#### Private Key

The Ed25519 private key is a 32-byte seed value.
Implementations derive expanded key material using the Ed25519 key generation procedure defined in RFC 8032.

Private keys are serialized using Bech32m with a dedicated HRP.

```text
private_key_string = bech32m(HRP="SECRET", TYPE="3", DATA="<private_key_data>")
```

#### Signature Format

Ed25519 signatures are 64 bytes long and consist of the concatenation of
`R` (32 bytes) and `S` (32 bytes).
Signature generation and verification follow RFC 8032.

### Derivation Path

For hierarchical deterministic key generation,
this proposal follows [SLIP-10](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
with a fully hardened derivation path.

```text
m / purpose' / coin_type' / address_type' / address_index'
```

Ed25519-based derivation does not support non-hardened child keys.
All components in the derivation path MUST be hardened.

#### Purpose

The purpose is set to `44`, following [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki).

Hardened derivation is used at this level.

#### Coin Type

The coin type is set to `21888`, which matches the PAC coin type registered in
[SLIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md).

Hardened derivation is used at this level.

#### Address Type

The address type is set to `3` for Ed25519 account addresses.

Hardened derivation is used at this level.

#### Address Index

Addresses start from index `0` and increase sequentially.

Hardened derivation is used at this level.

##### Example Paths

```text
m/44'/21888'/3'/0'   # first Ed25519 account/address
m/44'/21888'/3'/1'   # second Ed25519 account/address
```

## Test Cases

### Encoding Test Cases

The following test vectors demonstrate encoding and decoding of Ed25519 keys and addresses:

* **Private Key Data (hex)**: `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`
* **Public Key Data (hex)**: `03a107bff3ce10be1d70dd18e74bc09967e4d6309ba50d5f1ddc8664125531b8`
* **Address Data (hex)**: `0396a882c41ef85a07c75a6416a57fcce95aad4a3f`
* **Encoded Private Key**: `SECRET1RQQQSYQCYQ5RQWZQFPG9SCRGWPUGPZYSNZS23V9CCRYDPK8QARC0SW5D8X2`
* **Encoded Public Key**: `public1rqwss00lnecgtu8tsm5vwwj7qn9n7f43snwjs6hcamjrxgyj4xxuq5agu5g`
* **Encoded Address**: `pc1rj65g93q7lpdq0366vst22l7va9d26j3l2vr0em`
* **Message (bytes)**: `pactus`
* **Signature (hex)**: `1fc2c800499342d08242db9c3eb654027cb7b821e6af9ede56dfdb67e824f15bddb419d2db3fd5aaf3ef1a9ebb9a9deb749380f0d6a110cbe95319fe9f794305`

### HD Wallet Test Cases

For hierarchical deterministic wallet test vectors,
refer to [SLIP-0010](https://github.com/satoshilabs/slips/blob/master/slip-0010.md).

## Implementations

* [Go Implementation](https://github.com/pactus-project/pactus)
* [Rust Implementation](https://github.com/trustwallet/wallet-core)
* [Python Implementation (No HD Wallet)](https://github.com/pactus-project/python-sdk)
