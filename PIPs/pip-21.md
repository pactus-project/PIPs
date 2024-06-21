---
pip: 21
title: unbond token can rebond at any time.
author: Hui (@laosiji-io)
status: Rejected
type: Standards Track
category: Core
created: 15-01-2024
---

## Abstract

The purpose of this proposal is to make the staking token more liquid.

## Motivation

### Solving the problem of available score caused by the performance of node machines

Due to low node configuration and network issues, I need to migrate to a new high-end machine
But the available score is too low due to the previous low-end machine.
It may take up to 7 days to recover the score.
If it is possible to immediately change to a new staking address, So there's no need to wait that long.

### Fully leverage the role of tokens at any time

The current pledged tokens will not play any role within 21 days after unbond.
If you want to re-stake, you need to wait 21 days before doing so.

## Specification

### Keep current withdraw rules

1. The current withdraw rules are still retained.
2. If you need to withdraw token after unstaking, you still need to wait for 21 days.

### Can be rebond any time

1. Tokens can also be bonded during the waiting period.
2. Tokens from validator can also be bonded.
