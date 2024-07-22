---
pip: 28
title: Prevent Node Shutdowns for Validators in Committee
author: Javad Rajabzadeh (@ja7ad)
discussion-no: 163
status: Draft
type: Standards Track
category: Core
created: 06-07-2024
---

## Abstract

PIP-28 proposes to enhance Pactus blockchain stability by preventing active committee validators from shutting
down their nodes.

## Motivation

In the current CLI version, when we stop a node, we are not informed whether the validator is in the committee.
This oversight leads to penalties and a decrease in the validator's score. Preventing node shutdowns for active
committee members would address this issue, ensuring validators remain operational during crucial periods and
avoiding unintended penalties. This proposal aims to enhance the operational stability and reliability of the
Pactus blockchain by maintaining validator participation during their committee tenure.

## Specification

When stopping a node, the system should check if any validators are currently in the committee. If they are,
the user should be warn that specific validators are in the committee and informed that stopping the node will
result in penalties and a decrease in the validator's score. This check-and-warn mechanism will help prevent
unintentional disruptions and maintain validator performance during their committee duties.

### Check and Warn mechanism

In the check and warn mechanism, we need to track validators and know which
validator is currently in the committee. We should also monitor the interrupt
signal (Ctrl + C) from user input.

If some validators are in the committee, we show a confirmation warning before
shutting down the node; otherwise, we stop the node without a confirmation
request.

```shell
Warning: Some your validators are currently in the committee. Stopping the node
will decrease your availability score.

Do you want to continue? [y/N]
```

## Backwards Compatibility

No backward compatibility issues found.
