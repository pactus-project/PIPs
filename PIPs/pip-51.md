---
pip: 51
title: Supporting secp256k1 Curve
description: Add secp256k1 (ECDSA) support including encoding, addresses, and HD derivation
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
created: 2026-05-08
---

## Abstract

This PIP proposes adding support for the secp256k1 elliptic curve and the
associated ECDSA signature scheme. It defines address and key encodings for
secp256k1 key pairs, a fixed-size signature format, and a hierarchical
deterministic (HD) derivation path.

## Motivation

secp256k1 is the most widely used elliptic curve in blockchain ecosystems.
Adding native secp256k1 support in Pactus enables broader wallet interoperability,
reduces conversion cost for existing key material, and supports applications
already built on the curve.

Using deterministic ECDSA nonces according to RFC 6979 also improves resilience
against poor randomness in key generation and signing implementations.

## Specification

This proposal follows the secp256k1 curve parameters defined in [SEC 2](https://www.secg.org/sec2-v2.pdf)
and the deterministic ECDSA specification in [RFC 6979](https://tools.ietf.org/html/rfc6979).

### Address semantics

PIP-8 defines address type values by address usage.
This proposal introduces address type `4` as a new account address subtype for
secp256k1 public keys.

Implementations SHOULD treat addresses of type `4` as secp256k1 account addresses.
Existing BLS and Ed25519 address handling remains unchanged.

### Address Format

The address payload is derived from the compressed secp256k1 public key:

```text
address_data = ripemd160(blake2b_256(public_key))
```

Addresses are encoded with Bech32m.

```text
address_string = bech32m(HRP="pc", TYPE="4", DATA="<address_data>")
```

### Public Key

secp256k1 public keys are compressed to 33 bytes using the standard
`0x02`/`0x03` prefix notation.

Public keys are serialized with Bech32m using a dedicated HRP.

```text
public_key_string = bech32m(HRP="public", TYPE="4", DATA="<compressed_public_key>")
```

### Private Key

secp256k1 private keys are 32-byte values in the range `[1, n-1]`, where `n`
is the curve order.

Private keys are serialized with Bech32m using a dedicated HRP.

```text
private_key_string = bech32m(HRP="SECRET", TYPE="4", DATA="<private_key_data>")
```

### Signature Format

ECDSA signatures use the secp256k1 curve and follow these rules:

- Signature values are generated with deterministic nonce generation per RFC 6979.
- The signature is encoded as a fixed 64-byte sequence: `r || s`.
- The value `s` MUST be in the lower half of the curve order to ensure a
  unique canonical representation.

Verification follows the standard ECDSA verification algorithm over secp256k1.

### Derivation Path

For hierarchical deterministic key generation, this proposal follows [SLIP-10](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
and allows a non-hardened address index for secp256k1.

```text
m / purpose' / coin_type' / address_type' / address_index
```

### Purpose

The purpose is set to `44`, following [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki).
Hardened derivation is used at this level.

### Coin type

The coin type is set to `21888`, which matches the PAC coin type registered at
[SLIP-0044](https://github.com/satoshilabs/slips/blob/master/slip-0044.md).
Hardened derivation is used at this level.

### Address type

The address type is set to `4` for secp256k1 account addresses.
Hardened derivation is used at this level.

### Address Index

Addresses start from index 0 and increase sequentially.
This number is similar to the child index in
[BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) derivation.
Non-hardened derivation is used at this level to support public-key-only address generation.

Note: secp256k1-based derivation supports non-hardened child keys at the final address index,
which enables watch-only wallet support. The other levels MUST remain hardened.

#### Example paths

```text
m/44'/21888'/4'/0   # first secp256k1 account/address
m/44'/21888'/4'/1   # second secp256k1 account/address
```

## Backwards Compatibility

This proposal is compatible with existing Pactus address types by reserving a new
address type value for secp256k1 account addresses.
Existing BLS, validator, and Ed25519 address handling remain unchanged.

Clients and wallets that do not support secp256k1 will continue to operate normally
for existing address types, but they will not be able to parse or generate type `4`
addresses or secp256k1 key encodings.

## Security Considerations

secp256k1 is a widely deployed curve with extensive industry scrutiny.
Implementers must ensure private keys are generated uniformly and stored securely.

Deterministic ECDSA nonce generation per RFC 6979 reduces the risk of leakage
caused by poor randomness.

Special care must be taken to validate Bech32m HRPs and address type values
so secp256k1 account addresses are not confused with other address formats.

## Test Cases


## Reference Implementation

A reference implementation MAY be provided as separate source files or a supporting library.
