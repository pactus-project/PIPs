---
pip: 15
title: In-Memory Cache for Stored Items
status: Draft
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

### Account cache

Accounts can be cached by their address using an LRU (Least Recently Used) cache.

### Validator cache

All validators can be stored in a map. As the number of validators is not very large, we can keep them all in the map.
We need to create two maps: one to find validators by their number and another by their address.

### Public key cache

Public keys can be cached by their address using an LRU (Least Recently Used) cache.

### Recent transaction IDs

The most recent transaction IDs can be stored using a dequeue.
It's important to retain all transaction IDs up to the Time-to-Live (TTL) interval once the store is initialized.

### Recent Sortition seed

The most recent sortition seeds can be stored using a dequeue.
It's important to retain all sortition seeds up to the Sortition interval once the store is initialized.




