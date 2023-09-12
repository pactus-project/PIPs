---
pip: 7
title: Checking timestamp difference in handshaking
description: Check the timestamp difference between two peers before connecting to the network
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
status: Draft
type: Standards
category: Networking
created: 2023-09-12
---

## Abstract

For now, Pactus node implementations don't care about to time difference when connecting to each other and sometimes it brings some issues in network and sync modules, so, we can fix it by checking the timestamp difference in the hello message.

## Motivation

Checking the timestamp difference in handshaking and hello messages, can reassure us that none of the nodes in the network have a wrong time config.
Wrong time config can cause issues like calculating wrong `number of blocks left`.



## Specification

We should add a new field to our `hello` message called `mytime`, each node when receiving a `hello` message can check the `mytime` value of the message and calculate the difference between the message `mytime` and its timestamp.

Full nodes must drop `hello` message with a timestamp difference of more than `20 seconds`.

The result is when a node has a wrong timestamp config none of the other nodes accept `hello` message from it and it forces the node owner to fix the timestamp and we can make sure all nodes in the network have the same time.

## Security Considerations



## Copyright

Copyright and related rights waived via [CC0](../LICENSE).
