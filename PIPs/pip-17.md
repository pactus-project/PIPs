---
pip: 17
title: PNS Pactus Name System
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
status: Draft
type: Standards Track
category: PRC
created: 2023-12-17
---

## Abstract

This proposal suggests adding a TLD registry to the Pactus blockchain, allowing users to register TLDs and point them to a contract that manages them.

## Motivation

Adding the ability to point to an Pactus address, IP address, or other blockchain addresses using human-readable domain names can make sharing addresses secure and easier. It also improves the overall web3 experience on Pactus.

## Specification

### TLDs

The PNS system is similar to DNS on the internet, with two main components in Pactus: top-level domains (TLDs) and Registrars. Each TLD has three parts:

* Owner (a Pactus address)
* Name (the TLD itself, such as `.pac`)
* Registrar (a contact address that manages subdomains and resolving)

The nodes SHOULD keep track of TLDs, and provide RPC for finding Registrars of each TLD. time-to-live of this records should be 30 minutes.

Submitting a new TLD requires a transfer transaction to the treasury address with this structure:

* Memo: `TLD [name] [registrar]` (example: `TLD pac pc1zwqxz2wmz5upuvxzj3kpgfq3k2are4s3ctqxtxy`)
* Amount should be 10000 PAC coins to prevent random spam TLD registrations. 

> NOTE: memo limit is 64 characters in Pactus, and address contains 42 characters, so, we can define TLDs up to 17  characters.

The Owner MUST be able to change the contract by submitting the same name with a different contract address. Additionally, some other address MUST NOT be able to register the same TLD. any transaction with different style and lower amount MUST be considered as a normal transfer transaction.

The network/blockchain nodes SHOULD keep track of this PNS TLDs, index them (their owner, name and last registrar) and define RPC methods for resolving them.

### Registrars

A registrar contract SHOULD implement two main functions:

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
// ttl or time-to-live is in milliseconds, and this is up to registrar.
// Calling this function can be Owner(s) only and it's OPTIONAL.
fn resolve(name: String, ttl: u8) -> String;
```

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119 and RFC 8174.
