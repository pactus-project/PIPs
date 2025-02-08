---
pip: 38
title: Monitor Xeggex Deposit Account
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Standards Track
category: Core
created: 2025-02-07
---

## Abstract

This proposal suggests monitor the Xeggex deposit account due to suspicions of an
["exit scam"](https://en.wikipedia.org/wiki/Exit_scam) following the shutdown of the Xeggex exchange.

## Motivation

The recent shutdown of the Xeggex exchange has raised concerns about a potential exit scam.
At the time of the shutdown, a significant amount of Pactus coins—over 500,000 PAC,
representing approximately 50% of the circulating supply—was held in the Xeggex deposit account.

To protect the interests of affected users and the integrity of the Pactus network,
this proposal seeks to freeze the Xeggex deposit account while providing a secure mechanism
to unfreeze it if necessary.

## Specifications

The Xeggex account details are as follows:

```text
Deposit Address: pc1z2wtq43p8fnueya9qufq9hkutyr899npk2suleu
Watcher Address: pc1rqy07rwx7kdesnens3e5mc2ngk745q44wyndyc4
Account Hash:    31b863dcb0bb82184fb7357ae54c1e50c8984f5641eae1aff7a7b1f39284b9f5
Balance:         500,000 PAC
Freeze Height:   3,164,120
```

The address `pc1rqy07rwx7kdesnens3e5mc2ngk745q44wyndyc4` is designated as the
**Xeggex Deposit Watcher Account** and controlled by the Pactus team.

The Watcher account can exist in two distinct states, which determine the behavior of the Xeggex deposit account:

### 1. Frozen State

If the Watcher account has not signed any transactions (i.e., its public key remains unrevealed),
the Xeggex deposit account is considered **frozen**.
In this state, the Xeggex deposit account can only send transactions to the Watcher account,
and the transaction amount must exceed 500,000 PAC.
Transactions failing to meet this requirement will be rejected.

### 2. Unfrozen State

If the public key of the Watcher account is revealed (indicating it has signed and broadcast a transaction),
the Xeggex deposit account is considered **unfrozen** and can send transactions without restrictions.

To ensure proper enforcement during a network upgrade, nodes implementing this PIP will validate
the hash of the Xeggex deposit account when committing new blocks.
Nodes running the updated version will enforce the following rules if the account hash does not match the defined hash:

1. If the **public key of the Watcher account is revealed**, the Xeggex deposit account is unfrozen,
   and blocks can be committed as normal.
2. Otherwise, if the **Watcher account balance is less than 500,000 PAC**,
   the node will reject the incoming block and require the rest of the network to upgrade.

Once the majority of the network upgrades and adopts this PIP, the Xeggex account will be monitored
and controlled by the Pactus team. Any suspicious or malicious transactions will be rejected.

## Backward Compatibility

Nodes must upgrade to the latest version to enforce the new rules and avoid synchronization issues.
