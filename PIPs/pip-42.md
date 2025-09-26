---
pip: 42
title: URI Scheme
description: Define URI scheme for making Pactus payments.
author: |
  B00f (@b00f),
  Henry (@phoenixit99)
status: Draft
type: Informational
category: Interface
discussion-no: 241
created: 2025-06-06
---

## Abstract

This proposal introduces a standardized URI scheme for Pactus payments.

## Motivation

Uniform Resource Identifiers (URIs), as defined in [RFC-3986](https://datatracker.ietf.org/doc/html/rfc3986),
provide a standardized method for identifying resources on the internet.

This proposal defines a URI scheme for Pactus payments,
enabling users to initiate transactions effortlessly by clicking links on webpages or scanning QR codes.

## Specification

The proposed URI scheme follows this general format:

```text
pactus:<address>[?amount=<amount>][?memo=<message>]
```

### Components

* `pactus:`: The URI scheme identifier.
* `<address>`: A valid Pactus address.
* `amount` (optional): The amount to be transferred, specified in Pactus units.
* `memo` (optional): A message or note associated with the payment.

### Examples

**Basic Payment Request**:

```text
pactus:tpc1r35xwz99uw2qrhz9wmdanaqcsge2nzsfegvv555
```

**Payment with Amount**:

```text
pactus:tpc1r35xwz99uw2qrhz9wmdanaqcsge2nzsfegvv555?amount=123.45
```

**Payment with Amount and Memo**:

```text
pactus:tpc1r35xwz99uw2qrhz9wmdanaqcsge2nzsfegvv555?amount=123.45&memo=Invoice%20%1234
```

### Parsing Rules

1. Address: Mandatory. Must conform to Pactus address specifications.
2. Amount: Optional. Should be a positive decimal number.
3. Memo: Optional. Should be URL-encoded to ensure proper parsing.
