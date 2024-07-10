---
pip: 27
title: Pruned Node
author: Pactus Development Team <info@pactus.org>
discussion-no: 134
status: Accepted
type: Standards Track
category: Core
created: 22-06-2024
---

## Abstract

This proposal suggests supporting the "Pruned Node".
A "Pruned Node" can validate all new blocks and transactions, but it doesn't keep all the historical data.
Instead, it only retains the most recent part of the blockchain, deleting older data to save disk space.

## Motivation

Pruned nodes offer advantages such as saving storage space and syncing faster.
They can verify new transactions and blocks without storing the entire blockchain history.
Additionally, pruned nodes can download pruned data directly from a centralized server,
speeding up the syncing process compared to downloading the entire blockchain history.

## Specification

To support the Pruned Node feature, two questions should be answered:

1. Is this node a Pruned Node or a Full Node?
2. If it is a Pruned Node, how many blocks does the node need to keep or retain?

To answer the first question, we can check if the genesis block or block number one exists.
If it exists, the node is a "Full Node"; otherwise, the node is a "Pruned Node".

For the second question, we introduce a new parameter in the `Config` and name it `RetentionDays`.
This parameter indicates the number of days for which the node should keep or retain the blocks before pruning them.
It is only applicable if the node is in Prune Mode.
The minimum and default value is `10`.
This means blocks older than 10 days will be removed from the store.
There is no restriction for the maximum value.

The config should have a private method to calculate the `RetentionBlocks` based on `RetentionDays`.
The `RetentionBlocks` are the number of blocks that should be kept and not pruned.
Given that each day has almost 8640 blocks, the number of blocks to keep is `RetentionBlocks = RetentionDays * 8640`.

### pruneBlock Function

The `pruneBlock` function removes a block and all transactions inside the block from the store.
It is a private function and can't be accessed from outside the store.
It accepts a block height to prune, and returns a boolean that indicate
whether the block at the specified height existed and pruned, or did not exist, along with any encountered errors.

The `pruneBlock` function retrieves and decodes the block at the given height.
Once decoded, it deletes all transactions and associated keys related to the block from the store.

### Pruning Store

A Full Node can convert to a Pruned Node by pruning the store and removing old blocks.
Pruning the store is a time and resource consuming process and should not be performed while the node is running.
We need to add a new command named `prune` to `pactus-daemon` to prune an offline node.
A public method `Prune` should be defined in the store.
This method iterates over all blocks from the pruning height to the genesis block and prunes them.
The pruning height is `LastBlockHeight - RetentionBlocks`.

### Pruning on New Block

Once a new block is committed, the following operations should be performed:

1. If the node is a Full Node, no action is needed.
2. If the node is a Pruned Node, call the `pruneBlock` function
   with the block number equal to `LastBlockHeight - RetentionBlocks`.

This process ensures that for each new block added,
one old block will be removed, keeping the store blocks up to the `RetentionBlocks` number.

### Importing Data

Once a new node is initialized and before starting to sync with the network,
it can download and import pruned data from a centralized server.
This helps a pruned node sync faster.
After downloading the data, the data can be verified:

- All blocks should have a valid certificate.
- All transactions should have a valid signature.
- The state hash in the last block should be the same as the calculated state hash [^1] of the downloaded data.
- The last certificate should have a valid signature.

#### Import Data in Pactus Daemon

We need to add a new command named `import` to `pactus-daemon`.
The `import` command shows a list of available databases that can be imported from a centralized server.
Once the file is selected and downloaded, it can be imported.
If a database already exists, it should show an error before downloading.

#### Import Data in Pactus GUI

The GUI can import data once the node initialization is done and before syncing.
It can ask users if they want to run a Full Node or a Pruned Node.
If they want to run a Full Node, the procedure is the same as before.
If they want to run a Pruned Node,
a dialog will be shown with the server address and a list of available files to download.
Once the file is selected and downloaded, it can be imported.

## Exporting Data

To export data to a centralized server, we need to follow these procedures:

1. The server needs to run a Pactus Pruned Node with `RetentionDays` set to `10`.
2. At regular intervals, such as every week, the node will be stopped,
   a copy of the `RetentionDays` folder will be obtained and compressed.
3. The server will keep only the last 3 databases available for download and delete the rest.
4. It will update a JSON object to show the available databases for download.

## Backwards Compatibility

No backward compatibility issues found.

## Security Considerations

A pruned node can fully verify new blocks without any issues.
It retains more than 60,000 blocks, allowing it to calculate availability scores [^2].
Additionally, it can verify transaction lock-times [^3] since it has access to the last day's transactions.
An adversary may take control of the centralized server and manipulate all blocks and transactions.
However, the corrupted state can't be synced with the rest of the network.

## References

[^1]: [State hash](https://docs.pactus.org/protocol/blockchain/state-hash/)
[^2]: [Availability Score for Validators](http://pips.pactus.org/PIPs/pip-19)
[^3]: [Lock Time Transactions](https://pips.pactus.org/PIPs/pip-2)
