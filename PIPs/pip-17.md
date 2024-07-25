---
pip: 17
title: PNS Pactus Name System
author: Kayhan Alizadeh <me@kehiy.net>
status: Draft
type: Standards Track
discussion-no: 75
category: Network
created: 2023-12-17
---

## Abstract

This proposal suggests adding a TLD registry to the Pactus blockchain,
allowing users to register TLDs and point them to a contract that manages them.

## Motivation

Adding the ability to point to a Pactus address, IP address,
or other blockchain addresses using human-readable domain names can make sharing addresses secure and easier.
It also improves the overall web3 experience on Pactus.

## Specification

### TLDs

The PNS system is similar to DNS on the internet, with two main components in
Pactus: top-level domains (TLDs) and Registrars.
Each TLD has three parts:

* Owner (a Pactus address)
* Name (the TLD itself, such as `.pac`)
* Registrar (a contact address that manages subdomains and resolves them)

The nodes SHOULD keep track of TLDs, and provide RPC for finding Registrars of each TLD.
time-to-live of these records should be 30 minutes.

Submitting a new TLD requires a transfer transaction to the treasury address with this structure:

* Memo: `TLD [name] [registrar]` (example: `TLD pac pc1zwqxz2wmz5upuvxzj3kpgfq3k2are4s3ctqxtxy`)
* Amount should be 10000 PAC coins to prevent random spam TLD registrations.

> NOTE: The memo limit is 64 characters in Pactus, and
> the address contains 42 characters, so, we can define TLDs up to 17  characters.

The Owner MUST be able to change the contract by submitting the same name with a different contract address.
Additionally, some other addresses MUST NOT be able to register the same TLD.
any transaction with a different style and lower amount MUST be considered a normal transfer transaction.

The network/blockchain nodes SHOULD keep track of these PNS TLDs,
index them (their owner, name, and last registrar), and define RPC methods for resolving them.

### Registrars

A registrar contract SHOULD implement one main function:

Register:

```rs
// This function provides a way to register new domains like: blockchain.pac, 🔥.pac, and more.
// Calling this function can be Owner(s) only and it's OPTIONAL.
fn register(name: String, record: String) -> bool;
```

### Resolving by clients

The wallets, clients, and applications can use RPC nodes and resolve names
by reading the registrar contract storage related to it.
