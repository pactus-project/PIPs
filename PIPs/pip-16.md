---
pip: 16
title: Adding events in Pactus transactions
author: Kayhan Alizadeh <me@kehiy.net>
status: Draft
type: Standards Track
discussion-no: 73
category:
created: 2023-12-17
---

## Abstract

This document proposes adding an event section in contract call transactions,
that can be emitted by contracts. to be consumed by other services or other on-chain codes.

## Motivation

The motivation behind this proposal is to enhance the functionality of the Pactus blockchain by allowing contracts to
emit events within transactions.
This feature provides the ability to notify external systems or other on-chain
contracts about state changes or activities occurring within the blockchain.

## Specification

The Specification section below describes the syntax and semantics of the proposed feature.

### Syntax

The event section MUST be added as a new field in contract call transactions payload.
The syntax for this section is as follows:

```go
type Event struct {
  Name   string
  Data   map[string][32]byte
}

type Payload interface {
  // other methods.
  Events() []Event
}
```

The Events filed which is a list of Events will be added to transaction payload.
each event MUST contain a name with fixed length as memo and a map of string
(which is also fixed length as memo) pointing to a 32 byte data.

### Semantics

The event section in transactions allows contracts to emit events with associated data.
Events are identified by their name, and the data field holds the event-specific information.
emitting event MUST affect and increase the gas of contract call.

The event section is OPTIONAL, and if no events are emitted by the contract during a transaction,
the field can be omitted.

### Interface Examples

Here are sample code snippets showcasing how one can interact with the event section using Pactus interfaces:

```rust
mod MyContract {
  #[derive(kelk_event)]
    struct TransferEvent {
      from: String,
        to: String,
        amount: u8,
    }
}
```

`kelk_event` trait MUST contain an emit function.
