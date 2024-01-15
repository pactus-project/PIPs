---
pip: 21
title: unbond token can rebond at any time. 
author: hui (@laosiji-io)
status: Draft
type: Standards
category: validator
created: 15-01-2024
---

## Abstract

The purpose of this proposal is to make the staking token more liquid.

## Motivation

Because the time of unbond_interval takes too long, and when the token is unboned, these token will not have any effect.

## Specification

Tokens that have already been unbound can be rebond to other validator at any time. Withdrawal keep the original rules.
