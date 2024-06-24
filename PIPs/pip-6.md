---
pip: 6
title: In-Memory Storage of Public Keys, Validators, and Accounts using LRU Cache
status: Withdraw
type: Standards Track
discussion-no: 17
author: Javad Rajabzadeh <ja7ad@live.com>
category: Core
created: 2023-09-9
---
## Abstract

This proposal outlines the implementation of an LRU (Least Recently Used) cache to store
public keys, validators, and account data in memory base on review for
[PIP-4](https://pips.pactus.org/PIPs/pip-4).
Storing this information in memory will optimize performance and reduce the need for redundant data storage.

## Motivation

Efficiently managing public keys, validators, and account data is crucial for
reducing blockchain storage requirements and enhancing overall system performance.
Implementing an LRU cache will allow us to store frequently accessed data in memory,
reducing the need for repeated disk I/O operations.

## Specification

### LRU Cache Implementation

We will introduce an LRU cache to the Pactus project, which will be responsible for storing the following data:

1. Public Keys
2. Validators
3. Account Information

The LRU cache will have a defined capacity, ensuring that only the
most frequently used data is retained in memory.
When the cache reaches its capacity, the least recently used items will be evicted to make space for new data.

### Data Inclusion in the Cache

1. **Public Keys**:
   As transactions are committed for the first time, their associated public keys will be indexed by the signer's address.
   When a new transaction is processed, the cache will be checked for the presence of the signer's public key.
   If found, the public key will be retrieved from the cache, eliminating the need to include it in the transaction data.

2. **Validators**:
   Validators information will be loaded into the cache when the blockchain starts or when new validators are added.
   The cache will store validator data, including their public keys and other relevant information.

3. **Account Information**:
   Account data will be cached when accounts are accessed or updated.
   This will reduce the need for repeated disk reads when handling transactions involving specific accounts.

## Security Considerations

To ensure the security of the LRU cache, we need to consider the following:

1. **Cache Invalidation**:
   Proper mechanisms must be in place to invalidate cache entries when data is updated or removed.
   This ensures that outdated or incorrect data is not retrieved from the cache.

2. **Concurrency**:
   Handling concurrent access to the cache is crucial.
   We should implement appropriate locking mechanisms to prevent race conditions and data corruption.

3. **Memory Management**:
   Careful monitoring of memory usage is required to prevent excessive memory consumption by the cache.
   Implementing a sensible cache size limit is essential.

## Conclusion

By implementing an LRU cache to store public keys, validators, and account information in memory,
we aim to optimize the blockchain's performance, reduce disk I/O, and enhance the overall efficiency of our system.
This proposal outlines the key steps required to achieve this goal and
highlights security considerations to ensure the integrity of our cache.
