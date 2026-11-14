---
pip: 57
title: Anchor Request URI
description: A pactus:anchor URI that hands PIP-50 anchor values to a wallet, which builds and signs the transaction.
author: Midefos (@midefos)
status: Draft
type: Standards Track
category: Interface
created: 2026-11-01
requires: 42, 50
---

## Abstract

This PIP extends the `pactus:` URI scheme of [PIP-42](./pip-42.md) with a `pactus:anchor` URI
that carries the values of a [PIP-50](./pip-50.md) anchor transaction.
A website, app or QR code can hand those values to a wallet.
The wallet builds the transaction from the account the user picks, shows every field,
and signs only after the user approves.

## Motivation

PIP-50 anchors are created with a transaction (payload type 7),
but wallets have no way to receive one from a website.
Today a service can only give users an unsigned raw transaction. That has three problems:

- The wallet has to decode and trust a transaction someone else built, which is close to blind signing.
- The sender is fixed before the user has chosen an account.
- The transaction expires with its `lock_time` ([PIP-2](./pip-2.md)).

A URI with only the anchor values avoids all three.
It fits in a link or a QR code, and any wallet can support it in the same way.
It does not replace the node's `GetRawAnchorTransaction` (PIP-50):
it carries the user's intent to the wallet, which then builds the transaction with that API or on its own.

## Specification

The key words "MUST", "MUST NOT", "SHOULD" and "MAY" are to be interpreted as described in RFC 2119.

### Syntax

```text
pactus:anchor?<parameters>
```

- The URI uses the `pactus` scheme of PIP-42 with the reserved path `anchor`.
  PIP-42 payment URIs start with an address (`pactus:pc1…`), and no address equals `anchor`,
  so a wallet tells them apart by the path.
  Wallets that support only PIP-42 will reject `anchor` as an invalid address.
- Parameters follow RFC 3986 query syntax and are UTF-8 before percent-encoding.
  Values MUST be percent-encoded where needed (for example `ipfs%3A%2F%2F…`).
  `+` is a literal plus sign, not a space.
  Many standard query parsers follow HTML form encoding and turn `+` into a space
  (for example JavaScript's `URLSearchParams`, Python's `urllib.parse.parse_qs` and Go's `url.ParseQuery`),
  so implementations SHOULD split the query on `&` and `=` and percent-decode each value themselves.
- Parameter names MUST consist only of `a` to `z`, `0` to `9`, `-` and `_`, as written in the URI:
  names are not percent-decoded. This keeps `ACTION=…` or `%61ction=…` from slipping past
  as an unknown parameter next to the real `action`.
- Wallets MUST reject unknown parameters that start with `req-`, and SHOULD ignore other unknown parameters.

### Parameters

| Parameter | Required | Value |
|---|---|---|
| `network` | always | `mainnet` or `testnet`. Wallets MAY accept other network names they support (for example `localnet`) |
| `action` | always | `set` or `delete` |
| `type` | `set` | Anchor type, decimal integer from `0` to `255` (for example `1` for a service manifest) |
| `root` | `set` | Root hash, 32 to 64 bytes as hex (64 to 128 characters; the PAC-ANCHOR-1 hash is 32 bytes). Wallets MUST accept upper or lower case; writers SHOULD use lower case |
| `uri` | no | Manifest URI (for example `ipfs://<cid>`), at most 128 bytes of UTF-8. Default: empty |
| `locked` | no | Total deposit the anchor should have locked after the transaction, in PAC as in PIP-42's `amount` (for example `100` or `2.5`). Default: the PIP-50 `MinAnchorDeposit` (1 PAC) |
| `memo` | no | Transaction memo, as in PIP-42; at most 64 bytes of UTF-8 |
| `sender` | no | Suggested account. The wallet MAY preselect it, but the user can change it |

A `delete` URI carries only `network`, `action` and, optionally, `sender` and `memo`.
It MUST NOT contain `type`, `root`, `uri` or `locked`, so that a deletion cannot look like an update.

### Validation

A wallet MUST reject the whole URI, and MUST NOT offer to sign anything, when:

- the path is not `anchor`;
- a parameter name has a character other than `a`–`z`, `0`–`9`, `-` or `_`;
- a parameter appears more than once;
- `network` or `action` is missing or has an unknown value;
- for a `set`, `type` or `root` is missing;
- for a `delete`, `type`, `root`, `uri` or `locked` is present;
- a parameter is malformed or out of range:
   - `type` is not an integer from 0 to 255;
   - `root` is not 64 to 128 hex characters, or has an odd length;
   - `uri` or `memo` is not valid UTF-8, is too long, or contains a control or formatting character:
     Unicode general categories `Cc` (including ASCII `0x00`–`0x1F` and `0x7F`), `Cf`
     (for example U+202E RIGHT-TO-LEFT OVERRIDE or zero-width characters), `Zl` or `Zp`;
   - `locked` is not a plain decimal number of PAC (digits, optionally a `.` and 1 to 9 fractional digits;
     no sign, exponent, grouping or leading zeros), or is above `MaxNanoPAC`;
   - `sender` is not a valid bech32m account address for `network` (BLS, Ed25519 or secp256k1 account;
     validator addresses and the treasury cannot own an anchor).

Wallets MUST NOT silently fix or truncate a value.

### Wallet Behavior

A wallet that opens a valid `pactus:anchor` URI:

1. MUST refuse it if `network` does not match the wallet's network.
2. MUST let the user choose the sending account among its account addresses,
   and MUST show the account's current anchor, if any: its type, root hash, manifest URI and locked deposit.
   Whenever the user changes the account, the wallet MUST redo steps 4 to 6 for the new account
   (deposit to add, balance check, replacement warnings) before it can sign.
3. MUST build the transaction itself (payload type 7) from the parameters,
   for example with the node's `GetRawAnchorTransaction`.
   It sets the fee and `lock_time` as for any other transaction.
4. For a `set`, MUST compute the transaction's `Deposit` as described in [Deposit Semantics](#deposit-semantics),
   and MUST check that the account's balance covers it plus the fee.
   For a `delete`, the fee is taken from the refund (PIP-50), so the balance is not checked;
   the locked deposit must cover the fee (see step 6).
5. For a `set`, MUST show, before signing: network and account; anchor type, root hash and manifest URI;
   the deposit locked now and the amount this transaction adds; fee and memo.
   When the amount to add is above `MinAnchorDeposit`, the wallet MUST highlight it.
   It MAY warn when `type` is a reserved value (`4` to `254` in PIP-50), but MUST NOT reject the URI because of it.
   If the account already has an anchor, it MUST say that the anchor will be replaced.
   If that anchor has a different type, it MUST warn prominently:
   the account has a single slot, and the previous anchor (for example a DID document) will no longer be on chain.
6. For a `delete`, MUST refuse it if the account has no anchor,
   or if its `LockedDeposit` is below the fee (PIP-50 would reject the transaction).
   Otherwise it MUST show the anchor that will be removed (type, root hash, manifest URI)
   and the amount returned to the balance (the locked deposit minus the fee), as well as the fee and memo.
   It SHOULD warn when that amount is zero.
7. MUST NOT sign or broadcast without explicit user confirmation.

The URI has no return channel.
The wallet broadcasts the signed transaction through its own node, and the service learns of it by watching the chain
(for example the account's anchor, or transactions carrying its memo).
A memo is a hint, not proof: see [Security Considerations](#security-considerations).

### Deposit Semantics

In PIP-50, the `Deposit` of a `set` is added to the account's `LockedDeposit`,
and only a new anchor needs `MinAnchorDeposit`.
The service that builds the URI does not know which account the user will pick,
so it cannot know whether the `set` creates or updates an anchor.
The URI therefore states a target total, and the wallet, which knows the account, computes the amount to add:

```text
current = the account's LockedDeposit (0 if it has no anchor)
target  = max(locked, MinAnchorDeposit)   // locked defaults to MinAnchorDeposit
Deposit = max(0, target - current)
```

- New anchor, `locked` omitted: adds 1 PAC, the minimum.
- Update, `locked` omitted: adds 0, so users never lock more PAC by accident.
- `locked=100`: adds only what is missing to reach 100 PAC, whatever the account already has locked.

A target below what is already locked never releases funds: PIP-50 has no partial withdrawal, only `delete`.

### Design Notes

- **Values, not a raw transaction.** The wallet builds what it signs,
  so it can show meaningful fields, choose the account and set a fresh `lock_time`.
- **`network` is required**, so a testnet link cannot be signed on mainnet or the other way round.
- **Hex for `root`.** It matches how explorers display hashes and is URI-safe without encoding. Base64 is not.
- **A target total, not an amount to add.** The same link works for creating and for updating,
  so services do not need to know the account. It avoids both a failed creation (adding 0 to a new anchor)
  and an accidental extra lock (adding 1 PAC to an existing one).
- **PAC amounts, as in PIP-42.** `locked` uses the same unit as the payment URI's `amount`,
  so wallets parse both the same way. The 9 fractional digits map exactly to nanoPAC, so there is no rounding.
- **Reserved types are allowed.** PIP-50 says wallets must not reject a transaction because of its anchor type,
  so neither does this URI.
- **Words for `action`.** `set` and `delete` are self-describing in a link, while the on-chain values (0 and 1) are not.
- **Reject, don't repair.** A malformed link is more likely a bug or an attack
  than something the wallet should guess at.
- **No free-text label.** Unlike payment URIs, there is no `label` or `message`:
  text written by the link's author could mislead the user ("official refund…"),
  and the real fields already describe the transaction.

## Backwards Compatibility

No backward compatibility issues found. This PIP adds a URI format and does not change transactions or consensus.

## Test Cases

The [test vectors](../assets/pip-57/testvectors.py) include a reference parser and check every case below and more.
They use only the Python standard library.

### Valid URIs

Create or update a listing on mainnet. A new anchor locks 1 PAC; an existing one adds nothing:

```text
pactus:anchor?network=mainnet&action=set&type=1&root=2727edf1004e656e34a07948dfccde9ae583b5f240c88f9f5dc1ae36c5ae9261&uri=ipfs%3A%2F%2Fbafk2bzaceatsp3prabhgk3ruub4urx6m32nola5v6jamrd47lxa24nwfv2jgc&memo=pactus.page
```

The same listing, featured (100 PAC locked in total):

```text
pactus:anchor?network=mainnet&action=set&type=1&root=2727edf1004e656e34a07948dfccde9ae583b5f240c88f9f5dc1ae36c5ae9261&uri=ipfs%3A%2F%2Fbafk2bzaceatsp3prabhgk3ruub4urx6m32nola5v6jamrd47lxa24nwfv2jgc&locked=100&memo=pactus.page
```

Remove it (the locked deposit returns to the account, minus the fee):

```text
pactus:anchor?network=mainnet&action=delete&memo=pactus.page
```

In these examples `root` is the BLAKE2b-256 digest of the manifest (PAC-ANCHOR-1),
which is also the digest inside its CIDv1 (`raw` codec, `blake2b-256` multihash).

### Deposit to Add

With `MinAnchorDeposit` = 1 PAC. All amounts in PAC.

| Locked now | `locked` in the URI | Transaction `Deposit` |
|---|---|---|
| none (no anchor) | omitted | 1 |
| none (no anchor) | 0.5 | 1 |
| none (no anchor) | 100 | 100 |
| 1 | omitted | 0 |
| 1 | 100 | 99 |
| 100 | omitted | 0 |
| 100 | 1 | 0 |

A `delete` on an account with 100 PAC locked returns 100 PAC minus the fee to the balance.

### Rejected URIs

| URI (abbreviated) | Reason |
|---|---|
| `pactus:anchor?network=testnet&action=set&…` opened by a mainnet wallet | Network mismatch |
| `pactus:anchor?action=set&type=1&root=<64 hex>` | `network` missing |
| `pactus:anchor?network=mainnet&action=update&…` | Unknown `action` |
| `pactus:anchor?network=mainnet&action=set&root=<64 hex>` | `type` missing |
| `pactus:anchor?network=mainnet&action=set&type=256&root=<64 hex>` | `type` out of range |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<63 hex>` | `root` has an odd length |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<62 hex>` | `root` shorter than 32 bytes |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&uri=<129 bytes>` | `uri` longer than 128 bytes |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&memo=<65 bytes>` | `memo` longer than 64 bytes |
| `pactus:anchor?network=mainnet&action=set&type=1&type=2&root=<64 hex>` | Parameter repeated |
| `pactus:anchor?network=mainnet&action=delete&ACTION=set` | Parameter name not lower case |
| `pactus:anchor?network=mainnet&action=delete&%61ction=set` | Parameter name percent-encoded |
| `pactus:anchor?network=mainnet&action=delete&type=1&root=<64 hex>` | `delete` with `set` parameters |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&memo=a%0Ab` | Control character in `memo` |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&uri=ipfs%3A%2F%2F%E2%80%AEfdp.x` | U+202E in `uri` |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&locked=-1` | `locked` negative |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&locked=1e2` | `locked` not a plain decimal number |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&locked=0.0000000001` | More than 9 fractional digits |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&req-expiry=…` | Unknown `req-` parameter |
| `pactus:anchor?network=mainnet&action=set&type=1&root=<64 hex>&sender=<validator address>` | Validators cannot own an anchor |
| `pactus:anchor?network=mainnet&action=delete`, account without an anchor | Nothing to delete |
| `pactus:anchor?network=mainnet&action=delete`, account whose locked deposit is below the fee | PIP-50 would reject it |

## Reference Implementation

A reference parser, including bech32m address checks and the deposit computation,
ships with the [test vectors](../assets/pip-57/testvectors.py).

Pactus Pages produces these values for type-1 anchors today (currently as a `GetRawAnchorTransaction` request),
and will offer a `pactus:anchor` link and QR code once a wallet supports it.

## Security Considerations

- Anyone can publish a URI. Wallets MUST treat every value as untrusted text,
  display it without interpreting markup, and never open the manifest URI automatically.
- The confirmation screen is the security boundary.
  The user must see the full root hash, the manifest URI and the amount the transaction adds to the locked deposit.
  Services SHOULD show the same root hash and manifest URI next to the link or QR code,
  so users can check that what the wallet shows is what they asked for.
- Each account has a single anchor slot. A `set` replaces whatever is there, and a `delete` removes it.
  This is why wallets must show the current anchor and warn when its type changes.
- `locked` can lock a large amount, and getting it back takes a `delete`, which removes the anchor and costs a fee.
  This is why wallets must highlight the amount to add when it is above the minimum.
- Control and formatting characters are rejected because they can change how the confirmation screen reads:
  a newline can push text out of view, and a right-to-left override can reverse part of a URI.
- The manifest URI is free text on chain, and PIP-50 does not restrict its scheme.
  Wallets and explorers that render an anchor's URI as a link SHOULD do so only for schemes on an allow list
  (for example `ipfs://` and `https://`), and show anything else, such as `javascript:` or `data:`, as plain text.
- Memos are public and anyone can copy one, including from the mempool.
  A service that waits for a transaction MUST NOT link it to a user or session by its memo alone:
  it SHOULD check the resulting anchor (sender account, type, root hash and manifest URI) against what it expects.
- A link for another network is rejected rather than converted, so a testnet link can never move mainnet funds.
