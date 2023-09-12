---
pip: 7
title: Checking Timestamp Difference in Handshaking
description: Check the timestamp difference between two peers before connecting to the network.
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
status: Draft
type: Standards
category: Networking
created: 2023-09-12
---

## Abstract

Currently, Pactus node implementations do not consider time differences when connecting to each other. This oversight occasionally leads to issues in network and synchronization modules. To address this, we propose checking the timestamp difference in the hello message.

## Motivation

Checking the timestamp difference during handshaking and hello messages can ensure that none of the nodes in the network have incorrect time configurations. Incorrect time configurations can lead to problems such as inaccurately calculating the "number of blocks left."

## Specification

We propose adding a new field to our `hello` message called `mytime`. Each node, upon receiving a `hello` message, can examine the `mytime` value within the message and calculate the difference between the message's `mytime` and its own timestamp.

Full nodes must drop `hello` messages with a timestamp difference exceeding 20 seconds.

The outcome of this approach is that when a node has an incorrect timestamp configuration, other nodes will reject `hello` messages from it. This compels the node owner to rectify the timestamp issue, ensuring that all nodes in the network maintain consistent time settings.

## Security Considerations

Introducing a timestamp check during handshaking and hello messages can improve the security and integrity of the Pactus network. It is critical to prevent nodes with incorrect timestamp configurations from joining the network because they can potentially cause synchronization and consensus issues. Additionally, malicious actors may attempt to manipulate the timestamps of their nodes to disrupt network operations.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE).
