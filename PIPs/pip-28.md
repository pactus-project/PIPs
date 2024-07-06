---
pip: 28
title: Prevent Node Shutdowns for Validators in Committee
author: Javad Rajabzadeh (@ja7ad)
discussion-no:
status: Draft
type: Standards Track
category: Core
created: 06-07-2024
---

## Abstract

PIP-28 proposes a protocol change to prevent validators from shutting down their nodes while actively
serving in a committee. This measure aims to ensure continuous network stability and reliability by
maintaining the availability of validators during critical periods. By disallowing node shutdowns for
active committee members, the proposal seeks to mitigate potential disruptions and enhance the robustness
of the Pactus blockchain consensus mechanism.

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

## Backwards Compatibility

No backward compatibility issues found.
