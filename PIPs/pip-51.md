---
pip: 51
title: Protocol Upgrade Mechanism
description: Explain how Pactus performs protocol upgrades.
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Informational
created: 2026-05-08
---

## Abstract

This informational PIP describes the Pactus protocol upgrade mechanism.
A protocol upgrade is similar to a hard fork in Proof-of-Work blockchains:
it introduces backward-incompatible changes by raising the block version.

Nodes announce supported protocol versions during peer handshakes and block
proposals so validators can detect when a supermajority supports the upgrade
and safely activate the new block version.

## Motivation

Protocol upgrades are a necessary part of blockchain evolution.
In Pactus, they must be handled in a way that minimizes disruption while ensuring
that incompatible changes only become active when enough of the validating
network has signaled support.
This PIP explains how the upgrade process is signaled, decided, and activated.

## Specification

### Protocol Upgrade Definition

A protocol upgrade in Pactus is a backward-incompatible change that requires
nodes to run newer software.
The activation of such an upgrade is signaled by increasing the block version.

When the block version is increased, old nodes are no longer able to parse the
new blocks because they do not support the new block version.
As a result, old nodes cannot propose new blocks, and their proposals will be
rejected by the network.

### Version Announcement Channels

Nodes announce their supported protocol version through two mechanisms.

#### Handshake Phase

During the initial handshake between two directly connected peers, each node
advertises the latest protocol version it supports.

#### Proposal Messages

Whenever a proposer broadcasts a new block proposal, the proposal message also
carries the proposer’s latest supported protocol version.

### Network Version Snapshot

Each validator maintains a view of the network by recording supported protocol
versions from peers and proposals.
This snapshot reflects the distributed support level for the latest protocol
version among the validator set.

### Activation Threshold

A protocol upgrade is activated when a proposer detects that a supermajority of
committee validators support the latest protocol version.

Once this threshold is satisfied, the proposer increases the block version and
begins proposing blocks under the new version to other committee validators.
Because a supermajority of committee members now support the new block version,
those blocks are expected to be validated successfully.
Committee members that have not upgraded will not be able to commit the new
blocks and will gradually be replaced by upgraded validators through the
sortition process.

### Post-Activation Behavior

After the upgrade is activated, nodes that have not upgraded their software will
no longer be able to parse or validate new blocks produced under the new version.
These outdated nodes must upgrade to the latest software version in order to
rejoin the network and synchronize the chain.
