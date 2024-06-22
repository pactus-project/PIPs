---
pip: 24
title: Change Proposer on Double Proposing
author: B00f (@b00f)
status: Draft
type: Standards Track
category: Core
created: 10-05-2024
---

## Abstract

This proposal suggests initiating the "change proposer" phase [^1] once a second signed proposal is received,
regardless of its validity.

## Motivation

Based on some observations, we have discovered that some validators in the network are running duplicated nodes.
The current consensus detects double proposals and ignores them.
The procedure is as follows: Once an honest validator receives a proposal, it validates it. If valid,
it broadcasts a prepare vote to other validators.
Upon receiving a second proposal, the validator checks if they have already voted for a valid proposal.
If so, they simply ignore the second proposal to prevent double voting.

Sending a double proposal, in theory, should reduce the chances for validators to get rewarded.
For example, if validator _V<sub>b</sub>_ sends 2 valid proposals _P<sub>1</sub>_ and _P<sub>2</sub>_
to other validators, half of the network may receive _P<sub>1</sub>_ and the rest receive _P<sub>2</sub>_.
In this scenario, neither proposal can secure 2/3 of the prepare votes. Consequently,
validators will initiate a change in the proposer phase after some time.

However, in practice, the double proposer often still manages to get rewarded. Here are some reasons:

1. In some cases, one of the proposals is invalid, especially if the validator runs two different versions of Pactus.
   It is quite possible that the older version produces an invalid block.
   Since the majority of the nodes are running the latest version, the outdated proposal will get ignored,
   and only one proposal will be voted on.

1. Due to network topology and time differences between validators,
   one proposal can be received by the majority of the validators faster.
   Therefore, the first proposal can garner 2/3 of the votes before the second proposal causes vote divergence.

This proposal suggests starting the "change proposer" phase once the second signed proposal is received by the validators,
no matter its validity.
By doing so, validators will have no incentive to run duplicated nodes.

## Specification

## Backward Compatibility

## Security

## References

[^1]: [Change Proposer phase](https://docs.pactus.org/protocol/consensus/protocol/#change-proposer)
