---
pip: 18
title: Time Check Proposal
description: Implement Time Check on Node Startup
author: Mr. HoDL (@Mr-HoDL58)
status: Draft
type: Standards
category: Core
created: 28-12-2023
---

## Abstract

This proposal suggests the implementation of a time check feature during node startup.

## Motivation

Some users experience time discrepancies of more than 10 seconds in their system clocks, leading to handshake[^1] rejections by the network and preventing their nodes from syncing.

## Specification

We propose the addition of a time check feature to the software that verifies the system time at the node's startup.
If the time is inaccurate by more than +-10 seconds, it will issue a warning log in the command-line interface (CLI) and provide an on-screen alert in the graphical user interface (GUI).

To accomplish this, the time deviation between the local host and a randomly selected NTP[^2] server from the NTP Pool Project[^3] should be used. The NTP Pool Project is a globally distributed network of volunteer-operated time servers, ensuring precise time synchronization across various geographic locations.

## Security Considerations

The implementation of this time check feature should not compromise security.

## References

[^1] [PIP-7: Checking Timestamp Difference in Handshaking](https://pips.pactus.org/PIPs/pip-7)
[^2] [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
[^3] [NTP Pool Project](https://www.ntppool.org/)
