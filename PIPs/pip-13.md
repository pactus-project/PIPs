---
pip: 13
title: Import Private Keys
description: Import private keys to wallet
author: Amir Babazadeh (@amirvalhalla)
status: Draft
type: Standards Track
category: Core
created: 2023-11-27
---

## Abstract

Currently, the Pactus wallet does not support importing private keys. In this document, we propose a method to import private keys.

## Motivation

Importing private keys will give users the ability to store private keys inside the wallet.

## Specification

We propose adding a new `purpose` for imported private keys and setting it to 65535. The address index is an auto-incremental number that starts from zero and is an index in the imported private keys array. The address index is a hardened derivation and cannot be extended. whenever you import a private key, The address index is the length of the array.

## Advantage
  * Detect if the private key is imported or not from the path
  * The architecture helps to sort the addresses better

## Disadvantage
  * Inability to delete the private key if the user deletes the address (it destroys the structure of the private keys array order)
  * It is not compatible with hierarchical deterministic wallet.


### Example:
```text    
m/65535'/21888'/1'/0'  // imported validator address at index zero
m/65535'/21888'/2'/0'  // imported account address at index zero
```

[BIP32](https://pips.pactus.org/PIPs/pip-8)