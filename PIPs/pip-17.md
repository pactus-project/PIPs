---
title: PNS Pactus name system
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
status: Draft
type: Standards Track
category: Core
created: 2023-12-17
---

## Abstract

This proposal suggests adding a TLD registry to Pactus blockchain which people can register TLDs, pointing to a contract which manage them.

## Motivation

Adding possibility to point to some Pactus address, IP address or also other blockchains address to a humalreadable DNS like domain, can help people to share address and other stuff more safe and easier. also help everyone to have better and more secure web3 experience at Pactus.

## Specification

### TLDs

The PNS system is similar to DNS on internet, we have 2 main components in PNS. the first one is top level domains or TLDs. each TLD MUST be register by one address in Pactus. each TLD have 3 parts and nodes SHOULD keep track of them:

* Owner (which is a Pactus address)
* Name (which is the TLS itself like: `.pac`)
* Registrar (a contact address, which manage subdomains and resolving)

Submitting new TLD MUST follow a transfer transaction to treasury address, with this structure:

* Memo: `TLD [name] [registrar]`
* Amount should be 10000 PAC coins, we can make sure everyone won't register random TLDs. 

The Owner MUST be able to change contract by submitting the same name with different contract address. Also some other address MUST NOT be able to register same TLD.

### Registrars

A registrar contract SHOULD implement 2 main functions:

Register:

```rs
// This function provides a way to register new domains like: blockchain.pac, 🔥.pac and more. 
// Calling this function can be Owner(s) only and it's OPTIONAL.
fn register(name: String, Record: String) -> bool;
```

Resolve:

```rs
// This function provides a way to resolve PNS name to Record value. 
// for example: blockchain.pac => pc1zwqxz2wmz5upuvxzj3kpgfq3k2are4s3ctqxtxy 
// Calling this function can be Owner(s) only and it's OPTIONAL.
fn resolve(name: String) -> String;
```

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119 and RFC 8174.
