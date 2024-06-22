---
pip: 27
title: Pruned Node
author: Pactus Development Team <info@pactus.org>
discussions-to:
status: Draft
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

### Pruning Parameters

To support the Pruned Node feature, two questions should be answered:

1. Is this node a Pruned Node or a Full Node?
2. If it is a Pruned Node, how many blocks does the node need to keep or retain?

For the first question, we store a one-byte boolean `IsPruned` in the database.
This boolean indicates whether the store is pruned or not.
If `IsPruned` is not set yet or is set to `false`, the node is a "Full Node"; otherwise, it is a "Pruned Node".
Once the `IsPruned` value is set to `true`, it cannot be changed back to `false`.
This restriction makes sense because a "Pruned Node" cannot be changed to a "Full Node", though the reverse is possible.

For the second question, we introduce a new parameter in the `Config` and name it `RetentionDays`.
This parameter indicates the number of days for which the node should keep or retain the blocks before pruning them.
It is only applicable if the node is in Prune Mode.
The minimum and default value should be set to `10`.
This means blocks older than 10 days will be removed from the store.
There is no restriction for the maximum value.

The config should have a private method to calculate the `RetentionBlocks` based on `RetentionDays`.
The `RetentionBlocks` are the number of blocks that should be kept and not pruned.
Given that each day has almost 8640 blocks, the number of blocks to keep is `RetentionBlocks = RetentionDays * 8640`.

With these two parameters, we can implement the Pruned Node.

### PruneBlocks Function

First, we need to implement the `PruneBlocks` function for the store.
It is a private function and can't be accessed from outside the store.
The `PruneBlocks` function iterates over all blocks less than `CurrentHeight - RetentionBlocks`.
If a block doesn't exist, it breaks the loop;
otherwise, it removes the block and all transactions inside the block from the database.

### Pruning Database

A Full Node can convert to a Pruned Node by pruning the database and removing old blocks.
To do this, we add a public function `Prune` to the store, and it functions as below:

1. If `IsPruned` is set to `true`, no action is needed.
2. If `IsPruned` is set to `false`, then the value will turn to `true` and call the `PruneBlocks` function.

### Pruning on New Block

Once a new block is committed, the following operation should be done:

1. If `IsPruned` is set to `false`, no action is needed.
2. If `IsPruned` is set to `true`, then call the `PruneBlocks` function.

This process ensures that for each new block added, one old block will be removed,
keeping the store blocks number the same as the `RetentionBlocks` number.

<!--
  The Specification section should describe the syntax and semantics of any new feature.
  The specification should be detailed enough to allow competing,
  interoperable implementations for any of the current Pactus platforms.

  TODO: Remove this comment before submitting
-->

## Backwards Compatibility

<!--

  This section is optional.

  All PIPs that introduce backwards incompatibilities must include a section describing these incompatibilities and their severity.
  The PIP must explain how the author proposes to deal with these incompatibilities.
  PIP submissions without a sufficient backwards compatibility treatise may be rejected outright.

  The current placeholder is acceptable for a draft.

  TODO: Remove this comment before submitting
-->

No backward compatibility issues found.

## Reference Implementation

<!--
  This section is optional.

  The Reference Implementation section should include a minimal implementation that assists in understanding or implementing this specification.
  It should not include project build files.
  The reference implementation is not a replacement for the Specification section, and the proposal should still be understandable without it.
  If the reference implementation is too large to reasonably be included inline, then consider adding it as one or more files in `../assets/pip-####/`. External links will not be allowed.

  TODO: Remove this comment before submitting
-->

## Security Considerations

<!--
  All PIPs must contain a section that discusses the security implications/considerations relevant to the proposed change.
  Include information that might be important for security discussions, surfaces risks and can be used throughout the life cycle of the proposal.
  For example, include security-relevant design decisions, concerns, important discussions, implementation-specific guidance and pitfalls, an outline of threats and risks and how they are being addressed.
  PIP submissions missing the "Security Considerations" section will be rejected.
  A PIP cannot proceed to status "Final" without a Security Considerations discussion deemed sufficient by the reviewers.

  The current placeholder is acceptable for a draft.

  TODO: Remove this comment before submitting
-->
