---
pip: 18
title: Clock Offset Calculation
description: Calculate the difference between System Time and Network Time
author: |
    Mr. HoDL (@Mr-HoDL58)
    Mostafa Sedaghat Joo (@b00f)
status: Accepted
type: Standards
category: Core
created: 28-12-2023
---

## Abstract

This proposal suggests adding a time check feature to the Pactus blockchain.
This feature would alert users if their node's time is not synchronized with the network time.
Time is considered not synchronized if it deviates by one second or more from the network time.

## Motivation

Pactus nodes reject handshakes with nodes that have time discrepancies of
more than 10 seconds in their system clocks [^1].
This can help nodes diagnose if their time is misaligned by more than 10 seconds.
However, we currently lack a mechanism to alert users if
their node's time is misaligned by less than 10 seconds.

Some users notice their "Availability Scores" [^2] decreasing gradually.
One potential reason is that their system time is ahead of the network time.
Therefore, the timers within the consensus expire later, potentially causing users to sign blocks too late.
This delay could cause their signatures to arrive late compared to other validators.

## Specification

The proposal suggests adding a time check routine that repeats every minute.
This routine calculates the "Clock Offset" in each run,
which is defined as the estimated offset of the local system clock relative to the network's clock.
The network clock can be obtained using the Network Time Protocol (NTP) and a set of NTP servers from the NTP Pool Project.
The NTP Pool Project is a globally distributed network of volunteer-operated time servers,
ensuring precise time synchronization across various geographic locations.

To ensure a high degree of resilience against network errors,
the routine should iterate through the list of NTP servers.
In case all servers encounter errors, an error should be logged,
and the user should be notified that the "Clock Offset" is unavailable.

The "Clock Offset" value can be obtained and shown in different parts of the software,
such as the GUI, logs, and NodeInfo API.
If it deviates by one second, an alert will appear in the GUI or logs,
prompting the user to check and fix their system time.

## Security Considerations

The implementation of this time check feature should not compromise security.

## References

[^1]: [PIP-7: Checking Timestamp Difference in Handshaking](https://pips.pactus.org/PIPs/pip-7)
[^2]: [Availability Score for Validators](https://pips.pactus.org/PIPs/pip-19)
[^3]: [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
[^4]: [NTP Pool Project](https://www.ntppool.org/)
