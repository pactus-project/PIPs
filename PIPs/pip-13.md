---
pip: 13
title: Import Private Keys
description: Import private keys to wallet based on BIP44
author: Amir Babazadeh (@amirvalhalla)
status: Draft
type: Standards Track
category: Core
created: 2023-11-27
---

## Abstract

Currently, Pactus wallet does not support importing private keys. In this document, we propose a method to import private keys based on BIP44.

## Motivation

Importing private keys will give users the ability to manage their wallets securely.

## Specification

We propose adding a new coin_type to our BIP32 path ([here](https://pips.pactus.org/PIPs/pip-8)). The value of coin_type for imported private keys will be ffff (65535).

