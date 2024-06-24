---
pip: 7
title: Checking Timestamp Difference in Handshaking
description: Check the timestamp difference between two peers during the Handshaking phase
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
status: Final
type: Standards Track
discussion-no: 22
category: Network
created: 2023-09-12
---

## Abstract

Currently, Pactus nodes do not consider time differences when connecting to each other.
This occasionally leads to issues in the network and synchronization process [^1].
To address this, we propose checking the timestamp difference during the handshaking phase.

## Motivation

Checking the timestamp difference during handshaking can ensure that
most nodes in the network have a consistent time configuration.

## Specification

We propose adding a new field to the `hello` message called `my_time`.
Each node, upon receiving a `hello` message, can examine the `my_time`
value within the message and calculate the difference between the message's `my_time` and its own timestamp.

Non-faulty nodes must reject `hello` messages with a timestamp difference more or less than 10 seconds.

The outcome of this approach is that when a node has an incorrect timestamp configuration,
other nodes will reject `hello` messages from it.
This compels the node owner to rectify the timestamp issue,
ensuring that all nodes in the network maintain consistent time settings.

## Security Considerations

Introducing a timestamp check during handshaking with improve the security and integrity of the Pactus network.
It is critical to prevent nodes with incorrect timestamp configurations from
joining the network because they can potentially cause synchronization and consensus issues.

## References

[^1]: [Minus amount shown in front of "number of blocks left"](https://github.com/pactus-project/pactus/discussions/611)
