---
pip: 54
title: Safe Amount Validation for BatchTransfer
author: andrut <andrut@pactus.org>
status: Draft
type: Standards Track
category: Core
discussion-no: 297
created: 2026-06-09
---

## Abstract

This PIP documents the fix for a critical integer overflow vulnerability
in the BatchTransfer transaction type (PIP-39) that allowed minting coins
beyond the total supply, and specifies the chain recovery protocol used
to restore the network to a valid state.

## Motivation

The BatchTransfer payload introduced in PIP-39 contained a long-standing
bug that allowed minting coins out of thin air. This vulnerability was
identified through AI-assisted code analysis. Unfortunately, an attacker
discovered and exploited it first.

On June 9, 2026 at 10:07 UTC, the attacker crafted a BatchTransfer
transaction with 8 recipients, each assigned an amount of `2^61`
nano-PAC. The sum of 8 recipients overflows a 64-bit integer back to
zero:

```text
8 recipients × 2^61 nano-PAC = 2^64 nano-PAC
2^64 in 64-bit integer = 0  ← overflow
```

The network accepted the transaction believing the total transfer was
0 nano-PAC. In reality, each of the 8 recipient addresses was credited
with approximately 2.3 billion PAC.

**Total illegitimate PAC created: ~18.4 billion PAC**
**Pactus total supply: 42 million PAC**
**Cost to the attacker: 0.01 PAC in fees**

The fraudulently minted PAC represented more than 438 times the entire
legitimate supply of the network. The illegitimate balances cannot be
ignored or patched in place — they must be removed entirely via a chain
rollback to restore the integrity of the ledger.

## Specification

### Part 1: BatchTransfer Amount Validation Fix

Each recipient's amount MUST be validated against `MaxNanoPAC` during
`BasicCheck`:

```go
if recipient.Amount <= 0 || recipient.Amount > amount.MaxNanoPAC {
    return BasicCheckError{Reason: "recipient amount out of range"}
}
```

The sum of all recipient amounts MUST NOT exceed `MaxNanoPAC`:

```go
var total amount.Amount
for _, r := range payload.Recipients {
    if total > amount.MaxNanoPAC-r.Amount {
        return BasicCheckError{Reason: "batch transfer total amount overflow"}
    }
    total += r.Amount
}
```

| Check | Rule |
|-------|------|
| Per-recipient amount | `0 < amount <= MaxNanoPAC` |
| Aggregate amount | `sum(amounts) <= MaxNanoPAC` |
| Number of recipients | `1 <= count <= 8` (unchanged from PIP-39) |
| Duplicate recipients | No two recipients share the same address |

### Part 2: Chain Recovery Protocol

The chain rolls back to block **7,406,820**, the last valid block before
the exploit transaction at block 7,406,821.

The committee for block **7,406,821** is reset to a **Bootstrap
Committee**, which allows the network to resume block production
immediately without waiting for the full validator set to rejoin.
Validators from the existing 6,508 active validators gradually rejoin
the network as they upgrade to the patched software.

Once upgraded, the blockchain resumes automatically. No manual
intervention is required from node operators.

## Backward Compatibility

This proposal is not backward compatible. Any BatchTransfer transaction
where a recipient amount exceeds `MaxNanoPAC` is permanently rejected.

Activation requires a network hard fork. The chain rollback to block
7,406,820 and the Bootstrap Committee activation at block 7,406,821
constitute the hard fork boundary. All node runners must upgrade to
v1.15.5 or above.

## Security Considerations

This proposal addresses **CWE-190: Integer Overflow or Wraparound**.
Any arithmetic on user-supplied `Amount` values must be bounded by
`MaxNanoPAC` before computation.

The per-recipient cap makes the aggregate overflow check redundant in
practice since `8 × MaxNanoPAC` does not overflow `int64`. Both checks
are retained for defense in depth.

All transaction types performing arithmetic on `Amount` fields should
be audited for the same vulnerability class.
