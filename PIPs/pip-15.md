---
pip: 15
title: In-Memory Cache for Stored Items
status: Final
type: Standards Track
category: Interface
author: Mostafa Sedaghat Joo (@b00f)
created: 2023-12-03
---

## Abstract

This proposal suggests using in-memory caching systems within the store module to
enhance performance and reduce unnecessary decoding of data that is frequently accessed.

## Specification

This proposal suggests implementing different caching mechanisms for the following items within the store module:

### Account Cache

Accounts can be cached by their address using an LRU (Least Recently Used)[^1] cache.

### Validator Cache

All validators can be stored in a hash table[^2] (map). Since the number of validators won't be too large,
we can keep them all in memory.
We need to create two hash tables: one to find validators by their number and another by their address.
It's important to retain all validators once the store is initialized.

### Public Key Cache

Public keys can be cached by their address using an LRU (Least Recently Used) cache.

### Recent Transaction IDs

The most recent transaction IDs can be stored using the LinkedMap [^3].
It's important to retain all transaction IDs up to the Time-to-Live (TTL) interval[^4] once the store is initialized.
Once a new block is committed, the expired transactions can be removed from the LinkedMap.

### Recent Sortition Seed

The most recent sortition seeds can be stored using the PairSlice [^5].
A PairSlice is a slice where each item is a pair of a key and a value. The first item in the PairSlice represents the block height, and the second item represents the sortition seed.
It is important to retain all sortition seeds up to the Sortition Interval[^4] once the store is initialized.
If the slice reaches its maximum size, upon committing a new block, the oldest item in the slice can be removed to maintain the slice's fixed size.

## References

[^1]: [Cache replacement policies](https://en.wikipedia.org/wiki/Cache_replacement_policies)
[^2]: [Hash table](https://en.wikipedia.org/wiki/Hash_table)
[^3]: [Implementation of LinkedMap in Pactus](https://github.com/pactus-project/pactus/blob/main/util/linkedmap/linkedmap.go)
[^4]: [Consensus parameters in Pactus](https://pactus.org/learn/consensus/parameters/)
[^5]: [Implementation of PairSlice in Pactus](https://github.com/pactus-project/pactus/blob/main/util/pairslice/pairslice.go)
