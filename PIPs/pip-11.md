---
pip: 11
title: Deterministic key hierarchy for BLS12-381 curve
author: Mostafa Sedaghat Joo (@b00f)
status: Accepted
type: Standards Track
category: Core
created: 2023-09-26
---

## Abstract

This document describes hierarchical deterministic wallets (or "HD Wallets") for the BLS signature scheme.

## Motivation

Hierarchical deterministic key derivation is not yet standardized for the BLS signature scheme.
Given that BLS is widely used in many projects, having a hierarchical deterministic method is advantageous.
This document proposes a standard for generating HD key chains for the BLS signature scheme based on
[BIP-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki).

## Specification

We assume:

* n: Represents the order of G1 and G2 in
  [BLS12-381 curve](https://www.ietf.org/archive/id/draft-irtf-cfrg-pairing-friendly-curves-11.html#section-4.2.1),
  which is 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001.
* c: Represents the chain code used to derive the child key.
* P1: Represents a point in the G1 subgroup.
* P2: Represents a point in the G2 subgroup.
* point<sub>G1</sub>(p): Returns the point in the G1 subgroup resulting from EC point multiplication
  of the G1 base point with the integer p.
* point<sub>G2</sub>(p): Returns the point in the G2 subgroup resulting from EC point multiplication
  of the G2 base point with the integer p.
* ser<sub>32</sub>(i): Serializes a 32-bit unsigned integer i as a 4-byte sequence, most significant byte first.
* ser<sub>256</sub>(p): Serializes the integer p as a 32-byte sequence, most significant byte first.
* ser<sub>G1</sub>(P1):
  [Serializes](https://www.ietf.org/archive/id/draft-irtf-cfrg-pairing-friendly-curves-11.html#appendix-C)
  the point P1 as 48-byte sequence.
* ser<sub>G2</sub>(P2):
  [Serializes](https://www.ietf.org/archive/id/draft-irtf-cfrg-pairing-friendly-curves-11.html#appendix-C)
  the point P2 as 96-byte sequence.
* parse<sub>256</sub>(p): Interprets a 32-byte sequence as a 256-bit number, most significant byte first.

## Master key generation

To generate the master key, the
[KeyGen](https://www.ietf.org/archive/id/draft-irtf-cfrg-bls-signature-05.html#section-2.3) procedure described in
the BLS Signatures RFC is used.

Let S be a seed byte sequence of 128 to 512 bits in length.
This is the same as the seed byte sequence used in
BIP-0032.
The value of S should be the binary seed obtained from a
[BIP-0039](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) mnemonic and optional passphrase or it
should be the master secret obtained from a set of
[SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md) mnemonics and optional passphrase.

1. Calculate I = HMAC-SHA512(Key = "BLS12381 seed", Data = S)
2. Split I into two 32-byte sequences, I<sub>L</sub> and I<sub>R</sub>.
3. Use I<sub>R</sub> as master chain code.
4. Use KeyGen(I<sub>L</sub>) as master secret key

## Child key derivation (CKD) functions

Provided a parent extended key and an index i, calculating the corresponding child extended key is feasible.
The specific algorithm used for this computation varies based on the child being a hardened key or not (or equivalently,
whether i is greater than or equal to 2<sup>31</sup>), and on the type of keys involved, whether private or public.

### Private parent key &rarr; private child key

The function CKDpriv((k<sub>par</sub>, c<sub>par</sub>), i) &rarr; (k<sub>i</sub>, c<sub>i</sub>)
computes a child extended private key from the parent extended private key:

1. Check whether i ≥ 2<sup>31</sup> (whether the child is a hardened key).
   * If so (hardened child):
      * If public key is in G1: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = 0x00 \|\| ser<sub>256</sub>(k<sub>par</sub>) \|\| ser<sub>32</sub>(i)).
      * If public key is in G2: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = 0x01 \|\| ser<sub>256</sub>(k<sub>par</sub>) \|\| ser<sub>32</sub>(i)).
   * If not (normal child):
      * If public key is in G1: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = ser<sub>G1</sub>(point<sub>G1</sub>(k<sub>par</sub>)) \|\| ser<sub>32</sub>(i)).
      * If public key is in G2: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = ser<sub>G2</sub>(point<sub>G2</sub>(k<sub>par</sub>)) \|\| ser<sub>32</sub>(i)).
2. Split I into two 32-byte sequences, I<sub>L</sub> and I<sub>R</sub>.
3. The returned chain code c<sub>i</sub> is I<sub>R</sub>.
4. If parse<sub>256</sub>(I<sub>L</sub>) ≥ n or parse<sub>256</sub>(I<sub>L</sub>) + k<sub>par</sub> (mod n) = 0
   (resulting key is invalid):
   * let I = HMAC-SHA512(Key = c<sub>par</sub>, Data = 0x01 \|\| I<sub>R</sub> \|\| ser<sub>32</sub>(i)
      and restart at step 2.
5. Otherwise: The returned child key k<sub>i</sub> is parse<sub>256</sub>(I<sub>L</sub>) + k<sub>par</sub> (mod n).

In a BLS signature, the public key can be defined on either the G1 or G2 subgroups.
For hardened key derivation, to obtain different private keys,
we pad the private key with 0x01 in G<sub>1</sub> and 0x00 in G<sub>2</sub>.

### Public parent key &rarr; public child key

The function CKDpub((K<sub>par</sub>, c<sub>par</sub>), i) &rarr; (K<sub>i</sub>, c<sub>i</sub>)
computes a child extended public key from the parent extended public key. It is only defined for non-hardened child keys.

1. Check whether i ≥ 2<sup>31</sup> (whether the child is a hardened key).
   * If so (hardened child): return failure
   * If not (normal child):
      * If public key is in G1: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = ser<sub>G1</sub>(K<sub>par</sub>) \|\| ser<sub>32</sub>(i)).
      * If public key is in G2: let I = HMAC-SHA512(Key = c<sub>par</sub>,
          Data = ser<sub>G2</sub>(K<sub>par</sub>) \|\| ser<sub>32</sub>(i)).
2. Split I into two 32-byte sequences, I<sub>L</sub> and I<sub>R</sub>.
3. The returned child key K<sub>i</sub> can be calculated based on the public key subgroup.
   * If public key is in G1: point<sub>G1</sub>(parse<sub>256</sub>(I<sub>L</sub>)) + K<sub>par</sub>.
   * If public key is in G2: point<sub>G2</sub>(parse<sub>256</sub>(I<sub>L</sub>)) + K<sub>par</sub>.
4. The returned chain code c<sub>i</sub> is I<sub>R</sub>.
5. If parse<sub>256</sub>(I<sub>L</sub>) ≥ n or K<sub>i</sub> is the point at infinity (the resulting key is invalid):
   * let I = HMAC-SHA512(Key = c<sub>par</sub>, Data = 0x01 \|\| I<sub>R</sub> \|\| ser<sub>32</sub>(i))
      and restart at step 2.

## Test Cases

### Test vector on G1

Seed (hex): 000102030405060708090a0b0c0d0e0f

* Chain m
   * chain code: b879b097ba29929520a91dee29de1d94398c91076a4245be61704265d230c972
   * private: 4f55e31ee1c4f58af0840fd3f5e635fd6c07eacd14283c45d7d43729003abb84
   * public: 8fbed8842588b629377c0a0d0d9547a9ee17527d5fd6d2c609034a8c3c074dda031e0dfe886b454499bfe0f40a7c4b18
* Chain m/0<sub>H</sub>
   * chain code: 1b33156f5383050c5481396cc641be4e3436f2dae7cf68f5d78aec81c399e0b7
   * private: 5f5d7bfae7eabf2cc3faebc12449e1c7116c2777d7e384ead79df299667b8d9a
   * public: b2826a89a22fec3349d64f4379a1eb5632b0b345b985b738324a5b8db640307421201efe36ae6c8c639d32d4124496ae
* Chain m/0<sub>H</sub>/1
   * chain code: d74d25d225a40a3397798e554fc8dd0a80ce7f66f423c4cc0a6d4a278ee389c8
   * private: 3bea739c9a2695ba4af566bc3f28e5c62da8e721b977709f9d492f7129b83521
   * public: af5980f4172797c07174a4040eb0b1859b357b05f0a29ac65c35d957730fd722ffd520d861e8fbe3126d26ceb08dbe52
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>
   * chain code: c87a9057238d8c758f83df550d598678cfa9daaabe1abbe845c5847c60401e48
   * private: 221e1f998e9599aecdab1c9671162bea925ee50d5f1c5bca2ed19908ac0f2ddd
   * public: b06503dda77e1408478fc4b2d044a0ce2ab73691e8497a37f99d00e1076782698aacceb8e68fb9c3db6deccb0b8375fe
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>/2
   * chain code: 89c4994eb292ab70e6f3ae9b7882cca586062df242cad14c4f70af64c26cca42
   * private: 26a19ca5ff2f6b32871de71aabd87a30ce79cdde3b0556cbb46692295f0aee15
   * public: afd589792ba6bcb1866598a673a96fdaef9bf94026ef875a1a3e8d4fd839360f4659c9495afaf24c52577c0aa1fb5d45
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>/2/1000000000
   * chain code: 5f8b5e959ce7874b010b3250ff63c3860c005f73bb219ae7e53814a4d1e57c31
   * private: 44b743b059c2e4cb720378f4f0eda9369a1f02294e140e6a2e444bfdd36b1ad9
   * public: 99b404130a1ae6b6dd90ddf2a25c692f405536fee11046257ed6ba11629f101ad80658c61c039f0523de4c6e9f58a5c8

### Test vector on G2

Seed (hex): 000102030405060708090a0b0c0d0e0f

* Chain m
   * chain code: b879b097ba29929520a91dee29de1d94398c91076a4245be61704265d230c972
   * private: 4f55e31ee1c4f58af0840fd3f5e635fd6c07eacd14283c45d7d43729003abb84
   * public: b1bad3bf4a4ae87c89dec2c32512603ca08e2db62cfd2254c96bfe75068f5a98e7c4cd7d37cf0496dd6e79703e7c88e5046bdec9c896ef2ad030096bbcf73c6cff17add3da9530f22491901fdf7fd2076c0f08ea35a4fdaa00e7ac6d0a5442e3
* Chain m/0<sub>H</sub>
   * chain code: e271fa0804ffbc6ae5d63b31cce6cc5cc4b3e97b28672bf97a5b009174527938
   * private: 5695ba5087a27f8c0d7270455104658b2367b8e90ab6f7f57ac7ce22d4a6836c
   * public: b37da3080662ceeb7f07289801a56e5c555d413434ad096079c084caa162c8d224891f68816921f5bd1453af7d085bc400341d61ce496ffb11cd10f8e90522447fada1a5f646c45797e00460925876f0b63f4023bf27e828688f7b4dd833e641
* Chain m/0<sub>H</sub>/1
   * chain code: 4e0bae8832a7e12b6230ca296e252507ba55e4ca35fe413362f65256bd0adbc0
   * private: 555422bcbffd1d55eea6f87a924ba5d046bb60e2bffe2182daf78bab6a6e179f
   * public: b5f783bb1f1173feebb083f146c5a83470e84f26177862c5ab5b8be34ae6e3955d1b324f501a0d2751d971805f0612bc0b5e966c9060eeb08cf38a7e71037863ffb2f6433694e69db59f731dbe55125f995d2d6ccd139d56d5b481d3bce76baa
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>
   * chain code: e1132c2fdbca1bd9047e1db7eb9d98bc7559f2b853d20e8361553fbc8ba3a9b3
   * private: 39e4906c49c05f5daeed89ced104a32cda82782654dcc116346144424746f871
   * public: 81461b89b446d055ac3bc38b9384363cbabc47cc0a16c97a7c7ea24eeffd70f213daacdfd736a49c45befececcd8183212f04e186bcc9fbf67bfa5de862c57298cff4d36d5409380a166b9e37348b665186019b15498608309936e7ff36a87b5
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>/2
   * chain code: 2c430501360a9b6e7eb71a16774d887a48eea13e6eb513f40a2c7fa3b2771720
   * private: 3aa1e19a9bf2bf631d95b401e29d5f042160edd76ced9696e42a98be80b41faa
   * public: 92b20565b4a02bf82229f32e0ccc6f23446ded5ca2d67067afc70931b5a934f9469651e67e1105b5601cb585a1f44538124fe3529f5b1edb27ab44f0900e59a27f57df87aa03395a70825d02433c2498d8396c90986dad79d5ba9e0fc438bea8
* Chain m/0<sub>H</sub>/1/2<sub>H</sub>/2/1000000000
   * chain code: af0c9948f774376f0a8bd6df515b173d8d6d82b69a0d513797ee7ff283fd16ac
   * private: 2b01ef29730eb62c7114621d9d28ad77cf33f2434572a2bf9b73f1e502fea770
   * public: b05a01a80c3fe465227c23df7e36be1adcf557111f4cc50bf0f00c66c2b084d1e1d96e2f1c754496cb1f83dd1123456e17697e77a9b99ea557a63c9bf29668a966732882e7baebf079a4afad212910deb10e5151e18ae98ee4a57d0e622332aa

## Implementation

* [Python implementation to generate test vectors](/assets/pip-11/testvectors.py)
* [Go implementation](https://github.com/pactus-project/pactus/tree/main/crypto/bls/hdkeychain)

## References

* [BIP-0032: Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
* [BIP-0039: Mnemonic code for generating deterministic keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
* [SLIP-0010: Universal private key derivation from master private key](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
* [Pairing-Friendly Curves](https://www.ietf.org/archive/id/draft-irtf-cfrg-pairing-friendly-curves-11.html)
* [BLS Signature](https://datatracker.ietf.org/doc/draft-irtf-cfrg-bls-signature/)
