# Title: Transaction Lock Time

## Abstract

This document proposes adding a `LockTime` field to the transaction structure. The `LockTime` field indicates the block number at which the transaction can be unlocked and committed.

## Motivation

The current transaction structure in Pactus doesn't support for scheduled transactions. By introducing the `LockTime` field, users can set a block number at which a locked-time transaction can be unlocked and executed. With each block in Pactus having a fixed time interval of 10 seconds, users can ensure that their transactions are executed at nearly precise times in the future. This feature is similar to `nLockTime` in Bitcoin. However, in Pactus, it is mandatory to set it for all transactions, and it only accepts block numbers as input.

## Specification

The `LockTime` field is a mandatory 4-byte field that is added to the transaction structure after the `Stamp` field. If a transaction is intended to be unlocked in a future block, the `Stamp` field can be set to zero. For stamped transactions, the `LockTime` value should match the block number referenced by the `Stamp`.

While users have the option to set the `Stamp` field to zero for all transactions, there is a strong motivation for them to avoid doing so. Stamped transactions provide resistance against long-range attack.

Both locked-time and stamped transactions have a limited lifespan, and they become invalid once the time to live (TTL) interval expires.





# Title: Removing sequence field from transactions

## Abstract

This document propose to remove the `Sequence` field from the transactions.

## Motivation

The `Sequence` in Pactus is similar to the `nonce` in Ethereum.
It stops replay attacks by increasing the sequence number in the sender's account when a transaction is confirmed.
If the same transaction is replayed, it can be detected and rejected.
However, the sequence field makes it hard to implement the scheduled transactions.

This document proposes to remove the sequence field from transactions without compromising security.

## Specification

To detect a replayed transaction, we can check if it has been confirmed before. This involves looking up confirmed transactions and checking for any with the same hash. If a matching transaction is found, it means the transaction is replayed and can be rejected.

To ensure unique hashes for all transactions, relying solely on random stamp data is not enough. According to the Birthday Paradox, a 32-bit hash has a more than 50% chance of collision after 80,000 blocks.
A simple solution is to make the `LockTime` field mandatory for all transactions. The `LockTime` value should match the block number referenced by the Stamp.

### Light client implementation

A light client doesn't need to store the entire blockchain history. Since Pactus transactions have a limited lifespan, the light client can avoid keeping all transaction records. For example, with the current consensus parameters, the number of transactions in a single day is sufficient to detect replay attacks.



https://en.bitcoin.it/wiki/Protocol_documentation#tx
https://en.wikipedia.org/wiki/Birthday_attack