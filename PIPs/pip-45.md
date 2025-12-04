---
pip: 45
title: Structured Node Monikers
description: >
  Introduces structured key-value metadata for node monikers to provide
  richer, descriptive, and backward-compatible node identities.
author: Pactus Development Team <info@pactus.org>
status: Draft
type: Informational
category: Network
discussion-no: 269
created: 2025-10-07
---

## Abstract

This proposal enhances the Pactus node moniker field by introducing an
optional structured format that allows including multiple descriptive
attributes in a standardized, parseable way. The goal is to let node
operators provide additional metadata (such as name, email, or website)
while maintaining compatibility with the current plain string format.

## Motivation

Currently, node monikers in Pactus are limited to simple strings, e.g.
`"Javad"`. While this works for basic identification, it provides no
structured context for validators or operators, making it difficult to
associate contact information, organization name, or website with a
node.

A structured moniker format would allow nodes to self-describe in a
human-readable and machine-parseable way, improving transparency and
enabling tools to display enhanced validator metadata without requiring
on-chain extensions.

## Specification

To support both legacy and structured styles, the moniker field continues
to store a single string but can optionally follow a key-value pattern
for richer metadata. Nodes and clients may parse this format to extract
additional details while remaining compatible with existing monikers.

### Current Format

```ini
moniker = "Javad"
```

### Proposed Format

The structured format uses a **semicolon-separated key-value** scheme for
simplicity and safe parsing:

```ini
moniker = "name=javad;email=ja7ad@live.com;web=https://google.com"
```

- Keys and values are separated by `=`.
- Multiple entries are separated by `;`.
- Keys are case-insensitive and limited to alphanumeric and underscore
  (`_`) characters.
- Values can include alphanumeric, underscore, dash, and limited
  URL-safe characters.
- Plain monikers (e.g., `"Javad"`) remain valid and unchanged.
- Empty moniker (`""`) is still permitted.

### Example

| Example | Description |
|----------|--------------|
| `""` | Empty moniker |
| `"Javad"` | Basic string |
| `"name=javad;email=ja7ad@live.com;web=https://google.com"` | Structured metadata |

### Validation Rules

- Maximum length remains consistent with the current moniker field
  limit.
- Invalid pairs (missing key or value) are ignored during parsing.
- The first key-value pair’s `name` (if provided) is used as the display
  fallback in UI.

## Backwards Compatibility

This proposal is fully backward-compatible. Existing plain string monikers
require no change, and the structured format is entirely optional. Nodes
or clients unaware of this proposal will continue to display the full
string as-is without error.

## Security Considerations

- Node metadata is **public**, so sensitive information (e.g., personal
  email or phone numbers) should not be included.
- Clients and explorers must properly escape and sanitize displayed
  fields to avoid HTML or injection attacks.
- Structured parsing must strictly follow key/value delimiters and
  ignore malformed entries to prevent potential buffer or format issues.
