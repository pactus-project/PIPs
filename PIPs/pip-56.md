---
pip: 56
title: Native Assets
description: Fungible, non-fungible and semi-fungible assets as native Pactus state, capped per block to protect PAC.
author: CarbonFlake (@carbonflake)
status: Draft
type: Standards Track
category: Core
created: 2026-10-02
updated: 2026-10-11
requires: 39, 51, 54
---

## Abstract

This PIP adds native assets to Pactus with seven payloads, one new state tree and a cap per block, and nothing else:
no virtual machine, no committee, no new cryptography. An asset is a record with a symbol, a number of decimals, a
capped supply and a metadata hash. Balances are kept per account. Assets are signed, paid and replay-protected like
every other Pactus transaction, with the same accounts and keys.

| Payload | Does |
| --- | --- |
| `AssetCreate` | Creates an asset and credits its initial supply to the creator |
| `AssetAccept` | Opts the signer in to an asset against a refundable deposit. Nobody can receive units before accepting |
| `AssetAcceptFor` | Lets a sponsor pay the deposit and the fee of an acceptance that the account signed, so that an account with no PAC can opt in |
| `AssetClose` | Closes a balance of the signer, burning what is left if the signer allows it, and returns its deposit |
| `AssetTransfer` | Moves units to 1 to 8 recipients. A transfer to the zero address burns them |
| `AssetMint` | Lets the issuer create more units, up to the `MaxSupply` fixed at creation |
| `AssetSetRate` | Lets the issuer move the transfer rates of an asset, inside the bounds fixed at creation |

Fungible tokens, NFTs and semi-fungible tokens are the same record with different parameters, not different types.

**Nobody can be given an asset against their will.** An account holds an asset only after it has accepted it with its
own signature, and a deposit is locked for its record, by the account itself or by a sponsor that pays for a new user.
Transfers and mints never add a record to the state: they only change a balance that its owner opened. The owner gets
the deposit back when it closes a balance, and the freed place is reused. This is what stops unsolicited airdrops, and
it ties the number of balances in use to the PAC locked for them.

An asset may carry an optional **transfer policy**: a team rate and a burn rate, in basis points, that every transfer
applies with a few lines of integer arithmetic. The rates are variable but bounded: each has a minimum and a maximum
that are fixed at creation, and only the issuer can move a rate between them.

A sender can put up to 8 recipients in one transaction, which costs one signature for up to 8 transfers. Asset
transactions are ordinary entries of a block, and a block carries at most `MaxAssetTxPerBlock` (100) of them, so they
take at most 10 % of its 1 000 entries and PAC always keeps the rest. If asset traffic stays at that cap, a later
version can let the proposer pack asset transactions into bundles of one entry each (Future Extensions). A balance is
paid for with a deposit that is returned when it is closed; an asset record, which is permanent, is paid for once.
This PIP has no exchange, but it leaves room for one: section 6 reserves what a later PIP on liquidity pools needs, so
that such a PIP changes nothing here. It is meant for testnet first: mainnet waits for the testnet plan of the
Reference Implementation section.

## Motivation

Pactus has no smart-contract layer. A token today means a memo, an off-chain indexer, or another chain. Putting tokens
into consensus naively has two costs: tokens compete with PAC for the capacity of a block, and every validator stores
every balance, with no way to reuse the room of the ones that nobody uses any more.

This PIP keeps the design as small as the problem allows, in the spirit of Pactus: robust, reliable and light.

* **Robust.** Seven payloads and one rule per payload. Every amount is bounded and every sum checked before it is
  added ([PIP-54](./pip-54.md)). The only authorities an asset can have are a mint capped at creation and rates that
  move inside bounds fixed at creation.
* **Reliable.** Assets rest on the trust of PAC and on nothing else: the validators check every rule, and nobody else
  is trusted. Nothing depends on an operator, an indexer or an off-chain data store. The new rules are consensus code,
  though, and a bug in them can harm the whole chain, as [PIP-54](./pip-54.md) showed: hence the bounds, the tests,
  and the testnet plan that mainnet waits for (Reference Implementation).
* **Light.** No per-block hook, no new signature scheme, no epoch, no registry. The load that assets put on L1 is
  bounded by a constant, not by a market.

The commands are few: create, accept, close, transfer, mint, and set a rate. Exchanges, allowances, lending, oracles,
governance, freezing, clawback and metadata updates are outside this PIP; section 6 leaves room for a later PIP on
exchanges and liquidity pools.

## Specification

Integers are little-endian and fixed width unless a field is marked *varint*. `Address` is the 21-byte Pactus address,
and the zero address is the treasury address (21 zero bytes). An *account address* is a BLS, Ed25519 or secp256k1
account address: in this PIP the treasury address is never one, although the `IsAccountAddress()` of the node accepts
it, and neither is a validator address. `Hash` is BLAKE2b-256, the hash Pactus already uses, `||` is byte
concatenation, and a quoted string is its ASCII bytes. Fields are encoded in the order listed, using the encodings of
the existing payloads: `Address` as in `Transfer` (one byte for the treasury address), and *varint* as the `Amount` of
`Transfer` and the number of recipients of `BatchTransfer` ([PIP-39](./pip-39.md)). Decoding MUST consume exactly the
declared fields, and trailing bytes make a payload invalid. A *varint* MUST use its shortest encoding, and a longer
one is invalid, as the varint decoder of the node already requires, so that a payload has a single encoding. Every
count and length (recipients, symbol) MUST be checked against its bound before anything is allocated or read.
Byte-level test vectors come with the reference implementation.

### 1. Parameters

The values below are initial proposals for community review. They are constants of the protocol version in the node,
and a later version may change them ([PIP-51](./pip-51.md)). A change never alters an existing asset.

| Name | Value | Meaning |
| --- | --- | --- |
| `MaxAssetTxPerBlock` | 100 | Most asset transactions in one block, 10 % of its 1 000 entries. Bounds the entries and the work that assets take from a block |
| `MaxRecipients` | 8 | Recipients of one `AssetTransfer`, as `BatchTransfer` |
| `MaxDecimals` | 9 | Same as PAC |
| `MaxAssetSupply` | 2^63 - 1 | Largest quantity of any asset, the largest `int64` |
| `AssetCharge` | 0.1 PAC | Paid to the treasury, once, by every `AssetCreate`, for a record that is never removed (3.5) |
| `HoldingDeposit` | 0.1 PAC | Locked by every holding that is placed, and returned by `AssetClose` (3.5) |

### 2. State

#### 2.1 The asset tree

A new Merkle tree, `assetMerkle`, has the shape of `accountMerkle`, with its own hashing (below): a new record is
appended at the next index. The tree never shrinks and an `AssetRecord` never moves, so an `AssetID` never changes
meaning. A holding can be replaced, though: a balance that its owner closes becomes a free slot, and the next balance
reuses it. This PIP defines four kinds of record: a header at index 0, assets, balances (called holdings) and free
slots; the other kinds are reserved for later PIPs (section 6). `NoRecord` is the value `0xFFFFFFFF`. The tree holds
at most 2^31 records, at indexes 0 to 2^31 - 1, because the leaf index of the trees of the node is an `int32`;
`NoRecord` is therefore never an index, and a payload that would append a record to a full tree is invalid. The
deposits and `AssetCharge` keep the tree far below this bound (Security Considerations). Index 0 is the header, so no
`AssetID` is 0, and the `BasicCheck` of every payload of this PIP that names an asset rejects an `AssetID` of 0
(section 6 reserves it for PAC). The root depends only on the records: a node that rebuilds the tree from its store,
in whatever order it reads the records, MUST obtain the same root as a node that built it block by block, at every
size up to this bound.

`HeaderRecord` (kind `0`), 13 bytes in this PIP (section 6 lets a later version append fields), at index 0 from the
first block of version `V`:

| Field | Type | Notes |
| --- | --- | --- |
| `Kind` | `uint8` | `0` |
| `FreeHead` | `uint32` | Index of the free slot freed last, or `NoRecord` |
| `DepositTotal` | `int64` | PAC locked by the deposits of all holdings, in nano PAC |

`AssetRecord` (kind `1`), 82 to 93 bytes, or 123 to 134 with a transfer policy:

| Field | Type | Notes |
| --- | --- | --- |
| `Kind` | `uint8` | `1` |
| `Symbol` | `uint8` length, then bytes | 1 to 12 bytes of `A-Z0-9` |
| `Decimals` | `uint8` | At most `MaxDecimals` |
| `MaxSupply` | `int64` | Cap on `Issued`, fixed at creation |
| `Issued` | `int64` | Units created so far. Never decreases for an asset created by `AssetCreate` (section 6) |
| `Burned` | `int64` | Units destroyed so far. Never decreases for an asset created by `AssetCreate` (section 6) |
| `Issuer` | `Address` | The creator, an account address. The only account that may mint or set a rate. The zero address is reserved for assets of later PIPs (section 6) |
| `MetaHash` | 32 bytes | Hash of an off-chain description, fixed at creation. All zero if none |
| `PolicyPresent` | `uint8` | `0` or `1`. Fixed at creation |

If `PolicyPresent` is `1`, the record continues with the transfer policy:

| Field | Type | Notes |
| --- | --- | --- |
| `Collector` | `Address` | An account address that receives the team share. Fixed at creation. If it is not the issuer, the team rate starts at 0 and rises only once it has accepted the asset (sections 3.2 and 3.6) |
| `TeamRate` | 3 x `uint16` | `Current`, `Min`, `Max`, in basis points. `Min` and `Max` are fixed at creation |
| `BurnRate` | 3 x `uint16` | `Current`, `Min`, `Max`, in basis points. `Min` and `Max` are fixed at creation |
| `TeamCap` | `int64` | Largest team share of one transfer entry. `MaxAssetSupply` means no cap. Fixed at creation |

A basis point is 1/10 000, so a rate of 10 000 is 100 %. Only `Current` ever changes after creation. A rate is
**fixed** when `Min == Max` and **variable** otherwise, so no separate flag is needed. An asset without a policy
behaves as if both rates were 0.

`HoldingRecord` (kind `2`), 46 bytes:

| Field | Type | Notes |
| --- | --- | --- |
| `Kind` | `uint8` | `2` |
| `AssetID` | `uint32` | The index of the `AssetRecord` |
| `Owner` | `Address` | An account address |
| `Balance` | `int64` | Units held, `0 <= Balance <= MaxSupply` of the asset. May be zero |
| `Deposit` | `int64` | The PAC locked when the record was placed. `AssetClose` returns exactly this amount, out of which the close pays its fee |
| `LockedUntil` | `uint32` | The `Expiry` of the acceptance that placed the record (section 3.9), or 0. An `AssetClose` of the holding is valid only if `h > LockedUntil`, `h` being the height of the block |

`FreeRecord` (kind `3`), 5 bytes, the place of a closed holding:

| Field | Type | Notes |
| --- | --- | --- |
| `Kind` | `uint8` | `3` |
| `Next` | `uint32` | Index of the next free slot, or `NoRecord` |

The `AssetID` of an asset is the index of its `AssetRecord`. There is at most one `HoldingRecord` for a given
`(AssetID, Owner)`. In this PIP, only `AssetCreate` (for its signer, the creator), `AssetAccept` (for its signer) and
`AssetAcceptFor` (for the account whose signed acceptance it carries) place one, and a later PIP places one only with
the signature of the account that will hold it (section 6), so the signature of its owner is always behind a record.
`AssetTransfer` and `AssetMint` never place a record: they need the recipient's record to exist. Only `AssetClose`
removes one, and only for its owner. A node keeps a local index from `(AssetID, Owner)` to the record index. The index
is not consensus state and can be rebuilt from the tree.

**Hashing.** The tree has the shape of the trees of the node: a tree of one leaf has that leaf as its root, an inner
node hashes its two children, and the last node of a level of odd length is paired with itself. Its leaves and inner
nodes are hashed in separate domains, and a leaf commits to its index:

```text
leaf(i)    = Hash(0x00 || i || Bytes(record i))      (i as a uint32)
node(l, r) = Hash(0x01 || l || r)
```

The tag keeps a leaf from ever being taken for an inner node, whatever the length of a record, in this PIP or a later
one. The index keeps a record from being taken for the record at another index: two records can have the same bytes
(two `AssetRecord` with the same fields), and without the index a tree that ends with such a record could have the
same root as a tree with more copies of it, so the root would not commit to the number of records. The trees of
accounts and validators keep their hashing, and their roots do not change.

**Free slots.** The free slots form a stack: `FreeHead` is the slot freed last, and the `Next` of each slot is the
slot freed before it. When a holding is placed, it takes the slot at `FreeHead` if there is one, and `FreeHead` becomes
the `Next` of that slot; otherwise it is appended at the next index. When a holding is closed, its record becomes a
`FreeRecord` whose `Next` is the old `FreeHead`, and `FreeHead` becomes its index. An `AssetRecord` is always appended
and never takes a free slot, so that an `AssetID` is never an index that has held another record; in an `AssetCreate`,
the `AssetRecord` is appended first and the holding of the creator is placed after it. Every node obtains the same
indexes, because the order of the transactions of a block is fixed. The tree keeps the length of its peak: after many
balances have been closed, their slots stay as 5-byte free records and wait for the next balance.

#### 2.2 State root

For a block below the version `V` that activates this PIP, the state root is unchanged, and once a block of version
`V` is committed no block of a lower version is valid (Backwards Compatibility). For a block of version `V` or higher,
the root that the block header commits to, which is the state before the block as today, becomes:

```text
assetRoot = assetMerkle.Root()          (hashed as in section 2.1; the tree holds at least the header record)
stateRoot = HashMerkleBranches(HashMerkleBranches(accountMerkle.Root(), validatorMerkle.Root()), assetRoot)
```

Asset state MUST be part of the root: a store that the root does not cover would let two nodes commit the same block
with different balances. It is persisted in the same store batch as accounts and validators.

#### 2.3 Invariants

After every transaction, for every asset:

* `0 <= Burned <= Issued <= MaxSupply <= MaxAssetSupply`;
* the units held by its records equal `Issued - Burned`: in this PIP, the sum of its holdings;
* `Issued` and `Burned` never decrease, for an asset created by `AssetCreate` (section 6);
* if it has a policy whose `TeamRate.Current` is above 0, its `Collector` has a holding of the asset (sections 3.2,
  3.6 and 3.8).

And for the tree:

* a holding is placed only with the signature of its owner (in this PIP, by `AssetCreate`, `AssetAccept`, or
  `AssetAcceptFor`, which carries it), and removed only by `AssetClose`, for its owner, at a height `h > LockedUntil`
  and after burning what is left of its balance, so a transfer or a mint never changes the number of records or the
  PAC locked, and nobody holds a record that it did not sign for;
* the `Deposit` of the holdings add up to `DepositTotal`, and the PAC that accounts have lost to deposits is exactly
  `DepositTotal`: balances, stake, treasury and the PAC totals of the header (`DepositTotal` in this PIP) are
  conserved by every asset transaction, the fee being paid where the fee of any other transaction goes;
* the free slots, followed from `FreeHead` by `Next`, are exactly the records of kind 3, each reached once, and the
  chain ends with `NoRecord`; the header is the only record of kind 0, at index 0.

### 3. Payloads

Seven payload types are added, all of them signed by users. They take the next free numbers, 8 to 14, on the
assumption that [PIP-50](./pip-50.md) uses type 7; other Drafts also add payload types, so the editors renumber when
assigning. No test of this PIP depends on a type number.

```go
TypeAssetCreate    = Type(8)
TypeAssetTransfer  = Type(9)
TypeAssetMint      = Type(10)
TypeAssetSetRate   = Type(11)
TypeAssetAccept    = Type(12)
TypeAssetClose     = Type(13)
TypeAssetAcceptFor = Type(14)
```

#### 3.1 Rules common to all seven

* `Signer()` is `From`. Only **account addresses** (BLS, Ed25519, secp256k1) are valid. `BasicCheck` of every asset
  payload MUST reject the treasury address and validator addresses as `From`, with an explicit test and not through
  `IsAccountAddress()`, which accepts the treasury (Security Considerations).
* The transaction is signed, expires (its `LockTime` is valid for `TransactionToLiveInterval`, 8 640 blocks or one day
  on mainnet) and is protected against replay like every other transaction. No nonce is added. It is not one of the
  free transactions of the node (`IsFreeTx()`), so its fee follows the rules of a `Transfer`: consensus bounds it by
  `MaxNanoPAC`, and pools require their minimum, the fixed fee of 0.01 PAC by default.
* `Value()` is the PAC that the payload takes from `From` besides the fee (section 3.5): a charge that goes to the
  treasury, a deposit that is locked, or both. It is computed from the payload and the constants of section 1, without
  reading the state, and subtracted from `From` together with the fee. Every sum that involves `Value()`, the fee, a
  deposit or a balance MUST be rejected before it exceeds `MaxNanoPAC` ([PIP-54](./pip-54.md)). In this PIP,
  `AssetClose` is the one payload that gives PAC back to `From`.
* Every asset quantity is an `int64` with `1 <= quantity <= MaxAssetSupply`, except the `InitialSupply` of
  `AssetCreate` and the `MaxBurn` of `AssetClose`, which may be 0. A sum of quantities MUST be checked before it is
  added, in the form `total > MaxAssetSupply - amount`.
* An asset transaction is an ordinary transaction: it travels through the network and the pools, and sits in a block,
  as one. A block carries at most `MaxAssetTxPerBlock` of them (section 4).
* A recipient is an account address. Treasury and validator addresses are rejected, because nothing could move the
  units from them. The only exception is the zero address as a recipient of `AssetTransfer` (section 3.3). Any other
  recipient MUST already hold a `HoldingRecord` of the asset, possibly with a balance of 0: it MUST have accepted the
  asset (section 3.7).
* A payload that names an asset rejects an `AssetID` of 0 in `BasicCheck` (section 2.1).
* `PAC(a)` is the PAC balance of the account `a`, in nano PAC. A holding has its own `Balance`, in units of the asset,
  and the two are never mixed: a check on PAC always says `PAC(From)`.
* `Check` reads the state and changes nothing. `Execute` applies the whole transaction or none of it.

#### 3.2 `AssetCreate` (type 8)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | The creator, who becomes the issuer |
| `Symbol` | `uint8` length, then bytes | 1 to 12 bytes of `A-Z0-9`, and not `PAC` |
| `Decimals` | `uint8` | At most `MaxDecimals` |
| `InitialSupply` | *varint* `int64` | `0 <= InitialSupply <= MaxSupply` |
| `MaxSupply` | *varint* `int64` | `1 <= MaxSupply <= MaxAssetSupply` |
| `MetaHash` | 32 bytes | Opaque to consensus |
| `PolicyPresent` | `uint8` | `0` or `1` |
| `Policy` | as in section 2.1 | Only if `PolicyPresent` is `1`: `Collector`, `TeamRate`, `BurnRate`, `TeamCap` |

The record of the creator is placed if `InitialSupply > 0`, or if the policy is present and `Collector == From`.
`Value()` is `AssetCharge`, plus `HoldingDeposit` if the record of the creator is placed. `BasicCheck` of a policy:
`Collector` is an account address; if `Collector` is not `From`, `TeamRate.Current` is 0, and therefore so is
`TeamRate.Min` (see below); for each rate, `Min <= Current <= Max <= 10 000`; `TeamRate.Max + BurnRate.Max <= 10 000`;
at least one `Max` is above 0; `1 <= TeamCap <= MaxAssetSupply`. `Check`: `PAC(From) >= Value + fee`, and the tree has
room for the records that are appended (section 2.1).

`Execute`: debit `Value + fee`; credit `AssetCharge` to the treasury; append an `AssetRecord` with `Issuer = From`,
`Issued = InitialSupply`, `Burned = 0` and the policy as given; if the record of the creator is placed, place a
`HoldingRecord` of `From` with `Balance = InitialSupply`, `Deposit = HoldingDeposit` and `LockedUntil = 0`, and add
`HoldingDeposit` to `DepositTotal`. No record is placed for any other account, the collector included: the collector
is named by the creator but has not signed, so it must accept the asset itself (section 3.7). That is why a collector
other than the creator starts at a team rate of 0: the asset can be transferred at once, with no team share, and the
issuer raises the rate once the collector has accepted (section 3.6). A creator with `InitialSupply == 0` that is not
the collector holds no record yet: to mint to itself, it accepts the asset like anyone else.

The asset is **minting** if `MaxSupply > InitialSupply`. If they are equal, nobody can ever create another unit and
nobody holds any authority over its supply: the supply is fixed for ever. Symbols are labels, not names: they are not
unique, and the `AssetID` is the identity.

#### 3.3 `AssetTransfer` (type 9)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | The holder |
| `AssetID` | `uint32` | |
| `MaxRate` | `uint16` | Largest `TeamRate.Current + BurnRate.Current` that the sender accepts, in basis points |
| `NumberOfRecipients` | *varint* | `1 .. MaxRecipients` |
| `Recipients[].To` | `Address` | An account address, or the zero address to burn |
| `Recipients[].Amount` | *varint* `int64` | The gross quantity taken from the sender |

`Value()` is 0: a transfer appends no record, so it pays only the fee.

**Rates.** With a policy, each entry whose `To` is not the zero address is split as follows, with `D = 10 000`, the
current rates of the asset, and integer division throughout:

```text
share(a, r) = (a / D) * r + ((a % D) * r) / D
team        = min( share(Amount, TeamRate), TeamCap )
burn        = share(Amount, BurnRate)
net         = Amount - team - burn
```

`share(a, r)` is exactly `floor(a * r / D)`, written so that no intermediate value leaves the `int64` range: since
`r <= D`, `(a / D) * r <= a`, and `(a % D) * r < D * D`. No 128-bit product is needed. Because the two rates add up to
at most `D`, `team + burn <= Amount`, so `net >= 0`. Rounding is down, so a transfer too small to owe one unit of rate
owes nothing. Without a policy, `team` and `burn` are 0 and `net` is `Amount`. An entry to the zero address pays no
rate: the whole `Amount` is burned.

`BasicCheck`: `MaxRate <= 10 000`; the number of recipients is in range; no `To` appears twice; no `To` equals `From`;
every amount is in range; the sum of the amounts, checked as in section 3.1, does not exceed `MaxAssetSupply`.
`Check`: the asset exists; `TeamRate.Current + BurnRate.Current <= MaxRate` (both are 0 without a policy); `From` has
a holding of at least `total` units; every `To` that is not the zero address has a holding of the asset; `PAC(From) >=
fee`; no entry to an account has `net == 0`.

`Execute`: debit the fee in PAC; subtract `total` from the holding of `From` (the holding stays, even at zero, until
its owner closes it); then, for each recipient in the order of the list: if `To` is the zero address, add `Amount` to
the `Burned` of the asset; otherwise add `net` to the holding of `To`, add `team` to the holding of `Collector` if
`team > 0`, and add `burn` to `Burned`. If `team > 0` then `TeamRate.Current` is above 0, so the holding of
`Collector` exists, by the invariant of section 2.3; a node that does not find it has a fault and stops, as for its
index (section 5). Each addition applies to the live record, so the result is the same when addresses coincide. No
record is placed.

For example, with `Amount = 1 000 000`, `TeamRate = 200` (2 %), `BurnRate = 50` (0.5 %) and `TeamCap = 15 000`:
`share(Amount, 200) = 20 000`, so `team = 15 000`; `burn = 5 000`; `net = 980 000`. With `Amount = 99` and the same
rates, `team = 1`, `burn = 0` (0.495 rounds down) and `net = 98`. With `Amount = 49`, both shares round to 0 and the
recipient gets all 49.

`MaxRate` exists because a rate can change between the moment a user signs and the moment the transaction is included
(section 3.6). A wallet MUST set it to the sum of the current rates that it showed, and MUST NOT set it higher without
the explicit consent of the user: an issuer that sees a transaction with a loose `MaxRate` in the pool can raise the
rates just before it. The sender can never pay more than the bounds fixed at creation, and `MaxRate` narrows that
bound for one transaction. A transfer that fails because a rate moved is signed again with the new value.

A burn is a transfer to the zero address. It needs no payload of its own and cannot be undone: the units leave the
supply, and `Issued` is not lowered, so burning never makes room for a new mint.

#### 3.4 `AssetMint` (type 10)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | MUST be the `Issuer` |
| `AssetID` | `uint32` | |
| `To` | `Address` | An account address. Not the zero address |
| `Amount` | *varint* `int64` | |

`Value()` is 0. `Check`: the asset exists; `From == Issuer`; `To` has a holding of the asset; `Amount <= MaxSupply -
Issued`; `PAC(From) >= fee`. `Execute`: debit the fee; add `Amount` to `Issued`; add `Amount` to the holding of `To`. No
record is placed. A mint pays no transfer rate: it creates units, it does not move them.

The cap is on units ever issued, not on units alive. A holder can therefore read `MaxSupply` and know the largest
quantity that will ever exist. An asset with `MaxSupply == InitialSupply` rejects every mint.

#### 3.5 Charges and deposits

Two kinds of record cost PAC, and they are priced differently because they leave the state differently.

* An **asset record** is never removed: every holding refers to it by its index, and the index must keep its meaning.
  It is paid for once, by `AssetCharge`, which goes to the treasury and is not returned.
* A **holding** can be closed by its owner. It is paid for by `HoldingDeposit`, which is locked while the record
  exists and returned as it was posted to the owner of the holding, less the fee of the close, when `AssetClose`
  removes the record, even when a sponsor posted it (section 3.9). The locked PAC belongs to no account and is counted
  in `DepositTotal`.

What each payload takes from `From` besides the fee is computed from the payload and the constants of section 1, so a
wallet knows it before it signs and nothing depends on the state:

| Payload | `Value()` |
| --- | --- |
| `AssetCreate` | `AssetCharge`, plus `HoldingDeposit` if the record of the creator is placed (section 3.2) |
| `AssetAccept` | `HoldingDeposit` |
| `AssetAcceptFor` | `HoldingDeposit`, paid by the sponsor for the owner (section 3.9) |
| `AssetClose` | 0. The deposit comes back, less the fee (section 3.8) |
| `AssetTransfer`, `AssetMint`, `AssetSetRate` | 0 |

In this PIP, only creation and acceptance place records, so only they take PAC, and each record is paid for by the
account that signed for it, or by the sponsor of its acceptance. A charge or a deposit is always for a record that is
in fact placed.

**Where the PAC goes.** This PIP changes nothing about the fee. Every asset transaction pays it exactly as a
`Transfer` does, and it goes wherever the fee of any other transaction goes, whatever that path is or becomes: today,
the subsidy transaction pays the fees of a block, with the block reward, to its proposer (or, under
[PIP-49](./pip-49.md) delegation, possibly to the owner of its stake). Only `AssetCharge` is explicitly credited to
the treasury, and never to the proposer, so that a validator cannot refund the cost of the assets it creates itself. A
deposit is not paid to anyone: it is locked, and it comes back to the owner of the holding when it closes it, never to
a proposer; a sponsor that posts it gives it to the owner (section 3.9). Explorers that audit the supply MUST count
`DepositTotal`, and any PAC total that a later version adds to the header (section 6), next to balances and stake, as
they count the locked deposit of an anchor ([PIP-50](./pip-50.md)); leaving it out looks like a burn. The rates of
section 3.3 are a different thing: they are quantities of the asset, set by its issuer, and PAC is not involved.

#### 3.6 `AssetSetRate` (type 11)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | MUST be the `Issuer` |
| `AssetID` | `uint32` | |
| `NewTeamRate` | `uint16` | The new `TeamRate.Current`, in basis points |
| `NewBurnRate` | `uint16` | The new `BurnRate.Current`, in basis points |

`Value()` is 0. `Check`: the asset exists and has a policy; `From == Issuer`; `TeamRate.Min <= NewTeamRate <=
TeamRate.Max` and `BurnRate.Min <= NewBurnRate <= BurnRate.Max`; if `NewTeamRate` is above 0, `Collector` has a
holding of the asset, that is, it has accepted it; `PAC(From) >= fee`. `Execute`: debit the fee and set
`TeamRate.Current` and `BurnRate.Current` to the new values. Nothing else about the policy ever changes: not the
bounds, the cap or the collector. The new rates apply to every transfer included after this transaction in the same
block or later. A transaction that sets the current values again does nothing and obeys the same rules. There is no
nonce, so two `AssetSetRate` signed one after the other may be included in either order; an issuer that wants a given
final value waits for the first to be included before it signs the second.

An asset whose bounds satisfy `Min == Max` for both rates has fixed rates and can never be changed; its issuer holds no
authority over them. The bounds are a promise that anyone can read in the state, as `MaxSupply` is.

The rule on `NewTeamRate` above 0 keeps, with the rules of sections 3.2 and 3.8, the invariant of section 2.3:
whenever the team rate of an asset is above 0, its collector holds the asset. `AssetCreate` starts a collector other
than the creator at a team rate of 0, `AssetSetRate` cannot raise the rate while the collector has not accepted, and
the collector cannot close its balance while the rate is above 0. A team share therefore always has a holding to go
to, and no asset is ever blocked for lack of its collector, not even one whose collector address is wrong: its issuer
only never receives a team share. A collector that closed its balance at a team rate of 0 must accept again before the
rate can be raised.

#### 3.7 `AssetAccept` (type 12)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | The account that opts in. An account address |
| `AssetID` | `uint32` | |

`Value()` is `HoldingDeposit`. `Check`: the asset exists; `From` has no holding of the asset yet; `PAC(From) >=
Value + fee`; if there is no free slot, the tree has room for one more record. `Execute`: debit `Value + fee`; add
`Value` to `DepositTotal`; place a `HoldingRecord` of `From` for the asset with `Balance = 0`, `Deposit = Value` and
`LockedUntil = 0` (section 2.1).

Only the account itself can accept, because only its signature is valid. From then on it can receive transfers and
mints of the asset. There is no way to refuse a transfer once the record exists: an account that does not want an
asset simply never accepts it, and an account that accepted one by mistake closes the balance (section 3.8) and
gets its deposit back. Accepting twice is rejected, so nobody locks a deposit twice for the same record.

A sender cannot open a record for someone else without the signature of that account. With it, a sponsor may pay for
the record (section 3.9), which opens it but never lets the sponsor move its units. This has no exception: the
collector that a policy names accepts like anyone else, and until it has, the team rate of the asset stays at 0. Only
the issuer who named it is affected, so an account that is named as a collector against its will is not harmed and is
not obliged to do anything. An issuer that wants to distribute an asset publishes the `AssetID`, lets the recipients
accept, and then sends the units, in one batch of up to 8 per transaction. A wallet that wants to receive an asset
asks its user, then signs an `AssetAccept`, or an acceptance that a sponsor submits (section 3.9).

#### 3.8 `AssetClose` (type 13)

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | The owner of the holding. An account address |
| `AssetID` | `uint32` | |
| `MaxBurn` | *varint* `int64` | Most units that the owner agrees to burn with the close. `0 <= MaxBurn <= MaxAssetSupply` |

`Value()` is 0. `Check`: the asset exists; `From` has a holding of the asset with at most `MaxBurn` units;
`h > LockedUntil`, where `h` is the height of the block and `LockedUntil` that of the holding; the asset does not have
a policy whose `Collector` is `From` while `TeamRate.Current` is above 0; and the PAC condition below, with `Deposit`
the amount posted in the record. `Execute`: add the units of the holding to the `Burned` of the asset, with no rate,
as for a transfer to the zero address; change `PAC(From)` as below; subtract `Deposit` from `DepositTotal`; turn the
record into a `FreeRecord` and push it on the free stack (section 2.1). The units that were burned are gone with the
record, so the sum of the holdings still equals `Issued - Burned`.

```text
if Deposit >= fee:   Check    PAC(From) <= MaxNanoPAC - (Deposit - fee)
                     Execute  PAC(From) = PAC(From) + (Deposit - fee)
otherwise:           Check    PAC(From) >= fee - Deposit
                     Execute  PAC(From) = PAC(From) - (fee - Deposit)
```

Both branches give `PAC(From) + Deposit - fee` without ever forming that sum: `Deposit` and `fee` both lie in
`0 .. MaxNanoPAC`, so no subtraction is negative and no value leaves `0 .. MaxNanoPAC` ([PIP-54](./pip-54.md)), and a
close that leaves the balance at exactly `MaxNanoPAC` is valid.

The fee is taken from the refund, so that an account that has locked all its PAC can still close, as with the deposit
of an anchor in [PIP-50](./pip-50.md). The refund is the `Deposit` recorded when the holding was placed, not the
current `HoldingDeposit`, so a later change of that constant touches no existing record. The refund goes to the owner,
even when a sponsor posted the deposit (section 3.9).

Only the owner can close, because only its signature is valid. `MaxBurn` makes a close safe in both directions. With
`MaxBurn` at 0 the close needs an empty balance, and it fails if units have arrived since the owner signed, so it never
destroys a payment that the owner did not know about. With a larger `MaxBurn` the owner says, in its own signature,
how many units it agrees to lose: that is how it leaves an asset that it no longer wants, or ignores the dust that
someone sent it to stop it from closing, with one transaction and one fee. A holder that wants to keep an owner from
closing must therefore send more units than the `MaxBurn` that the owner chooses, and those units are burned, so the
grief is paid for with the attacker's own units. A wallet MUST show the units that a close burns before it signs.

The collector of an asset cannot close its balance while the team rate is above 0, because every transfer pays its
team share into that balance (section 2.3). When the team rate is 0 it may close, and then `AssetSetRate` cannot raise
the rate again until it has accepted the asset again (section 3.6).

A holding that a sponsored acceptance opened has the `Expiry` of that acceptance as `LockedUntil`, so its owner closes
it only from height `Expiry + 1`, once the acceptance has expired: until then the acceptance could open it again
(section 3.9). Since `Expiry` is at most `TransactionToLiveInterval` blocks after the height at which the holding was
opened, the lock lasts at most that long. Every other holding has a `LockedUntil` of 0 and can be closed at once.

A closed slot is reused by the next holding that is placed, so closing and accepting again does not grow the tree.

#### 3.9 `AssetAcceptFor` (type 14)

A Pactus transaction has one signer, and that signer pays. An account with no PAC therefore cannot send an
`AssetAccept`. `AssetAcceptFor` separates the consent from the payment: the account signs an acceptance, a short
message that costs nothing and needs no PAC, and a sponsor submits it in a transaction that the sponsor signs and pays
for.

| Field | Type | Notes |
| --- | --- | --- |
| `From` | `Address` | The sponsor. It signs the transaction and pays the fee and the deposit |
| `Owner` | `Address` | The account that accepts. An account address, not `From` |
| `AssetID` | `uint32` | |
| `Expiry` | `uint32` | The last block height at which the acceptance is valid |
| `OwnerPublicKey` | public key | The key of `Owner`, encoded as the public key of a transaction signed with that key type. Always present, since it is part of the payload |
| `OwnerSignature` | signature | The signature of `Owner` on the acceptance, encoded as the signature of such a transaction |

The acceptance is the message:

```text
Acceptance = "PAC-ASSET-ACCEPT-1" || GenesisHash || Owner || AssetID || Expiry
```

`GenesisHash` is the hash of the genesis document of the network, as the node computes it, so that an acceptance
signed for testnet is worthless on mainnet; the other fields are encoded as in the table. `Owner` signs these bytes
with its key, as it signs the sign bytes of a transaction. They start with a byte that starts no transaction (the
version of a transaction is 1), so an acceptance never verifies as a transaction, nor a transaction as an acceptance.

`Value()` is `HoldingDeposit`, paid by `From`. `BasicCheck`: `Owner` is an account address and is not `From`;
`OwnerPublicKey` is the key of `Owner`, checked as the node checks the key of the signer of a transaction. `Check`:
`Expiry >= h`, `h` being the height of the block, and then `Expiry - h <= TransactionToLiveInterval`, so that no sum
of heights is formed; `OwnerSignature` verifies on the acceptance, built with the genesis hash of the network, which
the node gives to `Check` so that `BasicCheck` needs no state; the asset exists; `Owner` has no holding of the asset
yet; `PAC(From) >= Value + fee`; if there is no free slot, the tree has room for one more record. `Execute`: debit
`Value + fee` from `From`; add `Value` to `DepositTotal`; place a `HoldingRecord` of `Owner` for the asset with
`Balance = 0`, `Deposit = Value` and `LockedUntil = Expiry` (section 2.1).

The deposit is a gift of the sponsor to the owner. The holding is an ordinary holding, locked only until the
acceptance expires (below): its owner closes it with `AssetClose` and gets the deposit back, less the fee of the
close, even with no other PAC (section 3.8), and the sponsor never gets it back. With the values of section 1, a
sponsor therefore pays 0.11 PAC to bring in a user, of which 0.1 PAC ends with the user, and it chooses whom it
sponsors, as a faucet does.

An acceptance lets its owner receive units of one asset, and nothing else: it never lets the sponsor, or anyone, move
units or PAC of the owner. Anyone who sees an acceptance can submit it and pay for it, and the owner gets its holding
either way.

**An acceptance opens at most one holding.** The holding that it opens keeps its `Expiry` as `LockedUntil`, and an
`AssetClose` of that holding is valid only if `h > LockedUntil` (section 3.8). As long as the acceptance is valid, the
holding that it opened therefore exists, and a second `AssetAcceptFor` that carries it fails, since `Owner` already
holds the asset, in the same block or a later one, whoever submits it and whatever signature it carries; once the
holding can be closed, the acceptance has expired. A holding that its owner closed is therefore never opened again
with the acceptance that opened it. The rule reads nothing but the asset tree: a node keeps no record of past
acceptances, and a restart, a snapshot or a sync changes nothing. Its price is that a sponsored holding can be closed
only after its acceptance has expired, at most `TransactionToLiveInterval` blocks after it was opened, so a wallet
SHOULD sign an acceptance with a short expiry, such as 360 blocks (one hour on mainnet), which is all the time that a
sponsor needs. An acceptance that no included transaction carried has opened nothing, and stays valid until its
expiry, as a transaction that was never included.

### 4. Block capacity

Asset transactions are ordinary entries of the list of transactions of a block. The body of a block, its decoder, its
limit of 1 000 entries and the transaction root that its hash covers keep their format.

#### 4.1 The cap

An *asset transaction* is a transaction whose payload type belongs to the asset layer: the seven types of section 3,
and those that later PIPs add to the layer (section 6). Two rules of block validity bound them:

1. A block of a version below `V` carries no asset transaction.
2. A block carries at most `MaxAssetTxPerBlock` asset transactions.

Every asset transaction of a block is otherwise checked and executed at its place as any transaction is: `BasicCheck`,
`Check`, `Execute`, its signature, its lock time, the replay check on its transaction ID and its fee, and only the
first entry of a block is a subsidy transaction. The count reads only the version in the header of the block and the
payload type of each entry. A validator makes it in `Block.BasicCheck`, right after the limit of 1 000 entries and
before it verifies any signature, so a block over the cap costs no more than reading it.

Whatever the senders, asset transactions take at most `MaxAssetTxPerBlock` entries of a block, 100 of its 1 000 with
the values of section 1, so PAC keeps at least 90 % of the entries of every block. In the worst case, a block of 1 000
entries holds the subsidy transaction, 100 asset transactions and 899 others. The same number bounds the work: each
asset transaction is verified, executed and written to the state as any transaction is. An `AssetAcceptFor` verifies
two signatures, the sponsor's and the owner's, so a block verifies at most 1 099 signatures instead of 999 today, and
blocks full of them are one of the worst cases of the benchmark that sets `MaxAssetTxPerBlock` (Reference
Implementation). Consensus sets no byte limit on a block. The gossip of the node caps a message at 1 MB, and a block
of 1 000 entries filled with the largest transactions, 100 `AssetTransfer` and 899 `BatchTransfer` with 8 recipients
each, is about 0.48 MB.

This is a consensus rule and not a fee market: whatever the demand for assets, it cannot take more than these entries
and this work from a block.

#### 4.2 Block building

PAC comes first: a proposer SHOULD take the other transactions first, and give asset transactions the entries that are
left, up to `MaxAssetTxPerBlock`, placing them after the others. It takes them from its asset pool in arrival order,
and skips any that does not pass `Check` against the state of the block under construction, keeping it in its pool,
since an earlier transaction of the same block can make a later one valid: an `AssetAccept` or an `AssetAcceptFor`
before a transfer to the account that signed it. A proposer SHOULD therefore try the skipped ones again after the
others. Only the asset transactions that it includes count against the cap. What does not fit stays in the pool for
the next block, until its lock time expires, and the signer then signs it again.

### 5. Node changes

* `Sandbox` exposes reads and writes of asset records, and the node adds the tree, its store prefix and the extended
  root. `executeBlock` gains no per-block hook: asset transactions are executed in place, like any other, and block
  validation applies the count of section 4.1.
* The local index from `(AssetID, Owner)` to a record is a cache, and execution is defined by the tree. A node MUST
  rebuild or verify it after an unclean shutdown, and MUST stop, not continue, when a lookup disagrees with the tree:
  two nodes with different indexes would disagree on the validity of a block.
* Acceptances need no store of their own: their single use follows from the `LockedUntil` of the holding that they
  open (section 3.9), which is in the asset tree, so restarts, snapshots and sync carry it with the tree, and the
  replay check of transactions does not change.
* Block building follows section 4.2. The proposer counts the asset transactions that it includes, after their checks,
  not the candidates that it takes from its pool.
* Transaction pool: a pool is local policy, not consensus. Implementations SHOULD give asset transactions their own
  pool, as each payload type has one today, so asset transactions cannot crowd out payments and payments cannot evict
  them, and SHOULD let it hold at least `MaxAssetTxPerBlock` transactions (10 % of the default `MaxSize` of 1 000, the
  share of the pool of `BatchTransfer`, taken from the other pools so that their shares still add up to `MaxSize`): a
  proposer builds its block from its pool, and a smaller pool could not fill the cap. Fee estimation (`CalculateFee`)
  gives the same fixed fee as for a `Transfer`, and a wallet adds `Value()` to show the total PAC that a transaction
  takes. A pool MAY drop an `AssetTransfer` or `AssetMint` whose recipient has not accepted the asset, but only when
  no transaction in the pool can make it valid (an `AssetAccept` or `AssetAcceptFor` of that recipient), since a
  proposer includes both in one block (section 4.2). A pool SHOULD run the checks in the order of their cost:
  `BasicCheck`, then the PAC balance (for an `AssetClose`, the PAC balance plus the deposit that it returns, since it
  pays its fee from the refund), then the signature, then the asset-state `Check`. It SHOULD also limit the number of
  pending asset transactions per sender, because each one can be valid alone against the current state while all
  together are not (several transfers of the same units), and without a limit one funded account can fill the pool
  with transactions that the proposer will skip.
* RPC (mandatory for the official node, on every surface it ships): payload type values `8` to `14` in `PayloadType`;
  `GetRaw*Transaction` builders for the seven payloads, the one for `AssetAcceptFor` taking an acceptance signed by
  its owner; `GetAssetState`, returning the fields of the header (`FreeHead`, `DepositTotal` and any total that a
  later version adds) and the number of records of the tree; `GetAsset`, returning the fields of section 2.1, the
  policy with its current rates and bounds and whether its collector has accepted it (the team rate cannot rise above
  0 before), and the live supply `Issued - Burned`; and `GetAssetBalance(AssetID, Address)`, which tells an account
  that has not accepted the asset, or has closed it, from one that holds a balance of 0, and returns the `LockedUntil`
  of a holding, so that a sender can check before it signs and an owner knows when it can close. A node SHOULD also
  offer a list of the balances of an address from its local index.
* Wallet: the wallet of the node builds and signs an acceptance (section 3.9) only after showing the asset, its
  issuer, the expiry and that the holding cannot be closed up to that height, gives it a short expiry by default (360
  blocks), and can submit an `AssetAcceptFor` for an acceptance that it receives.
* Explorers that audit the supply MUST add `DepositTotal`, and any PAC total that a later version adds to the header,
  to balances, stake and the treasury: that PAC belongs to no account, and leaving it out looks like a burn.
  `AssetCharge` goes to the treasury, and every other PAC amount keeps its place.

### 6. Room for later PIPs

This PIP has no exchange. A later PIP, for example one for liquidity pools in the style of PancakeSwap v2, adds
payloads and records to the asset layer. The rules below let it do so without changing any record, payload or
invariant of this PIP. The values that they reserve are invalid in this PIP and cost nothing.

1. **Asset transactions.** The payloads that a later PIP adds to the asset layer are asset transactions (section 4.1),
   and they count in `MaxAssetTxPerBlock` with those of this PIP. A later PIP may give its own payloads a lower cap
   inside `MaxAssetTxPerBlock`, so that they cannot crowd out transfers.
2. **Records.** Record kinds 4 to 255 are reserved for later PIPs, and no payload of this PIP creates one. Records of
   every kind live in the asset tree, under its root. Only holdings take free slots: a record of any other kind is
   appended and never moves, so that its index can serve as its identity, as the `AssetID` does. Records of every kind
   are hashed as in section 2.1, so their encodings may have any length.
3. **Units outside holdings.** A later PIP may define records that hold units of an asset, such as the reserves of a
   pool. The invariant of section 2.3 counts them: the units held by all the records of an asset equal its
   `Issued - Burned`.
4. **PAC outside accounts.** A later PIP may define records that hold PAC, such as the PAC side of a pool. It then
   appends a total of that PAC to the header, as `DepositTotal` is the total of the deposits. A later version may
   append fields to the header in this way, and rewrites the header in the longer encoding at its first block. Every
   PAC total of the header belongs to no account, and the conservation of section 2.3 and the supply audits of
   sections 3.5 and 5 count them all.
5. **PAC in a pair.** No asset has the `AssetID` 0, and every payload of this PIP that names an asset rejects it. A
   later PIP may use the `AssetID` 0 to name PAC, for example in a pair or a path of swaps.
6. **Assets without an issuer.** `AssetCreate` always sets an account as `Issuer`, so no asset of this PIP has the
   zero address as `Issuer`. A later PIP may create such assets, for example the shares of a pool. No `AssetMint` or
   `AssetSetRate` can ever pass for them, since `From` is never the treasury, and the PIP that creates them defines
   how their `Issued` and `Burned` move, as long as the first two invariants of section 2.3 hold: the bounds, and the
   conservation of units. The third invariant, which makes `MaxSupply` a cap on the units ever issued (section 3.4),
   is a promise of the issuer of an asset created by `AssetCreate`.
7. **Signatures, opt-in and charges.** The payloads of a later PIP follow section 3.1. They credit units only to a
   holding that its owner opened or to records of their own PIP, they place a holding only with the signature of the
   account that will hold it, in a transaction or in an acceptance, with `HoldingDeposit` and, for an acceptance, its
   `Expiry` as `LockedUntil` (section 3.9), they remove a holding only for its owner and only at a height
   `h > LockedUntil`, and they compute `Value()` from the payload and the constants, never from the state. The opt-in
   of this PIP and its rules on charges therefore stay true.
8. **Rates.** A payload that moves units between a holding and another record applies to them the split of section
   3.3, bounded by a `MaxRate` that the owner of the holding signs, or its PIP says why it does not. The team share
   goes to the holding of the collector, which exists whenever the team rate is above 0 (section 2.3).

### 7. Conventions (informative)

Nothing here is checked by consensus. Wallets and explorers agree on it so that one record can serve several uses.

| Use | `Decimals` | `MaxSupply` | `InitialSupply` | Notes |
| --- | --- | --- | --- | --- |
| Fungible token | 0 to 9 | any | any | `MaxSupply == InitialSupply` for a fixed supply |
| NFT | 0 | 1 | 1 | One unit. Its `AssetID` is its identity |
| Semi-fungible edition | 0 | N | N | N identical units. A smaller `InitialSupply` leaves room for mints |

* `MetaHash` is the hash of a document that gives the name, description, image and attributes. A wallet fetches the
  document from where the issuer published it and checks the hash. The memo of the `AssetCreate` transaction MAY carry
  a pointer to it, within the memo length.
* A collection is a list of `AssetID`s that the issuer publishes off-chain, for example in a document committed by a
  [PIP-50](./pip-50.md) anchor. The protocol has no collection object.
* A wallet shows the **net** amount that a recipient will get, not only the gross `Amount`, and the bounds of the
  rates, not only their current values. A royalty or a tax on units of an asset, paid to a collector, is expressed
  with `TeamRate`; a deflationary asset is expressed with `BurnRate`. Rates are meant for fungible assets: on an asset
  of supply 1 every share rounds to 0. An issuer that wants its team share paid to another account names that account
  as `Collector`, creates the asset with a team rate of 0, and raises the rate once the collector has accepted the
  asset; or it names itself, which needs no extra step, and forwards the share when it wants.
* Receiving an asset takes two steps: the recipient accepts, then the sender sends. A wallet asks its user before it
  signs an `AssetAccept`, and MAY offer the acceptance as a link or a QR code that carries the `AssetID`. An
  application that brings in users with no PAC sponsors their acceptances: the wallet signs an acceptance, which needs
  no PAC, and the application submits it with `AssetAcceptFor` and pays the deposit, which the user gets when it
  closes the balance, at the earliest once the acceptance has expired. A distribution to many accounts is a claim: the
  issuer publishes the `AssetID`, accounts accept, and the issuer sends to those that did, 8 at a time. A sale of an
  NFT starts with the buyer accepting it. A wallet shows the deposits as locked PAC, never as spendable PAC, and
  SHOULD offer to close the balances that the user no longer wants, which returns their deposits, showing the units
  that each close would burn.

## Rationale

**On-chain, because that is the simplest thing that is also fully trusted.** An asset rule that every validator
checks adds no assumption to Pactus. An earlier draft of this PIP ran the assets off-chain under a bonded committee
that checkpointed them on Pactus. That keeps L1 capacity free, but it adds operators, bonds, slashing, epochs and
quorums, and its correctness and its data availability rest on a federation that Pactus cannot check. The hard cap of
section 4 answers the same worry about L1 capacity with one counter.

**A cap, not a market.** A fee market needs a price that nobody knows before the layer is used. A cap on the number of
asset transactions in a block needs no guess, is trivial to validate and gives PAC a floor that no demand can lower.
Its price is that asset users can be delayed when asset demand reaches the cap. That is acceptable, and the cap is one
constant that a later version can raise. Because asset transactions are plain entries, one number bounds both the
entries and the work that assets take from a block.

**One record for every kind of asset.** A token-ID dimension (items inside a collection) needs item records, per-item
supply and more rules for each type. Here an NFT is an asset with a supply of one. The cost is that a collection of N
items is N creations, each priced by the fee and `AssetCharge` and paced by the cap. A later PIP can add collections if
there is demand, without changing these records.

**Batching inside a transaction.** `BatchTransfer` already shows that up to 8 recipients are a safe size. Inside
`AssetTransfer`, one signature then moves up to 8 transfers, which is the batching that really lowers the work, since
it saves signatures. The single-recipient transfer is the case of one.

**No bundles in this version.** A proposer could pack the asset transactions of many senders into one entry of a
block, as a bundle: an unsigned transaction that carries signed transactions, built like the subsidy transaction. It
would let asset traffic grow past the entries that the cap gives it, but it saves entries only, not signatures, bytes
or state writes, and a transaction that carries transactions is new to every part of the node that reads a block:
execution, the store and its stripped public keys, sync, the pools, gRPC, ZMQ and the history of the wallet. With a
cap of 100 asset transactions, PAC keeps 90 % of every block without bundles. They are left to a later version, if
asset traffic stays at the cap, after a prototype in the node (Future Extensions).

**Burn is a transfer.** It saves a payload type, a pool and an RPC builder, and the semantics are unambiguous. The
cost is that a transfer to the zero address by mistake cannot be undone, which wallets guard against.

**Mint capped at creation.** Issuers need minting (editions, game items, a stablecoin). Holders need a bound. A cap
that is fixed at creation, and that burning does not reopen, is a promise that anyone can read in the state.
`MaxSupply == InitialSupply` is the strongest form and has no mint authority at all. Transferring or renouncing the
issuer role is left out: it adds a payload and a way to lose control by mistake.

**No allowance.** The approve and spend-from pattern is where most user losses on token chains happen. Leaving it out
keeps the trust model simple: only the holder can move units, and nobody else can ever be allowed to.

**Transfer rates: variable, but inside bounds that cannot move.** Issuers of fungible assets ask for a share of each
transfer (a team or royalty share) and for a burn. A rate that nobody can change is too rigid, since an issuer may need
to lower it, and a rate that its issuer can change freely is a trap. So each rate has a `Min` and a `Max` fixed at
creation, public in the state like `MaxSupply`, and the issuer moves only the current value between them. `Min == Max`
gives a rate that is fixed for ever, with no authority at all. The calculation is three lines of integer arithmetic,
rounds down, never leaves the `int64` range, and a sum of the two rates of at most 100 % means `net` is never negative.
`MaxRate` in the transfer protects the signer against a change that lands before inclusion. The rates act on units
of the asset only and have nothing to do with PAC fees.

**One issuer for mint and rates.** An earlier draft had a separate parameter controller, a per-parameter mutable flag
and a minimum received per transfer. Here `Min < Max` already says that a rate is variable, one `MaxRate` per
transaction replaces the minimum per recipient, and the issuer is the only authority. A separate controller (a
multi-signature or a vote) can be added later without changing the records.

**Opt-in, so that nobody is given an asset against their will.** Anyone can create an asset with any symbol, and
without opt-in anyone could put it in any wallet for a fee that is small in PAC: look-alike symbols, links in
metadata, and a record added to every victim's state. With opt-in, an asset reaches an account only if that account
signed for it. It also simplifies the rules. A transfer or a mint never places a record, so their execution has no
creation order to fix, their charge is 0, and a holding is placed only when its owner asks and locks a deposit. The
cost is two steps to receive an asset, and a recipient that needs a little PAC for the deposit before it can accept,
unless a sponsor pays it (section 3.9). To the knowledge of the author, the XRP Ledger, Stellar and Algorand also ask
the receiver to opt in. There is no exception: the creator's own record is placed by the creation it signed, and the
collector named by a policy must accept like anyone else. Creating the collector's record at creation would let an
issuer put an asset on any account by naming it. Instead, a collector other than the creator starts at a team rate of
0, the issuer raises the rate only once the collector has accepted, and the collector cannot close its balance while
the rate is above 0. A team share therefore always has a holding to go to, and no asset can be blocked for lack of its
collector, not even by a mistyped address: such an asset only never pays a team share. The price is that a team rate
fixed for ever above 0 (`Min == Max`) needs the issuer as its own collector, which can then forward the share.

**A sponsor may pay, but only the owner consents.** A Pactus transaction has one signer, who pays, so the opt-in alone
would keep every account with no PAC from receiving anything: the main friction of this design for new users.
`AssetAcceptFor` separates the two roles. The owner signs an acceptance, off-chain and for free, and a sponsor submits
it and pays. The opt-in stays whole, since a record still needs the signature of its owner, and an acceptance only
lets its owner receive: unlike a permit on token chains, it never lets anyone spend, so a user tricked into signing
one loses nothing. An acceptance opens at most one holding, because that holding cannot be closed before the
acceptance expires, so a holding that its owner closed is never opened again with it. The single use is thus a
property of the state, not of recent history: a set of used acceptances, kept as the IDs of recent transactions are,
would make the validity of a block depend on blocks that the state root does not cover, and on every snapshot that
carries them (Alternatives Considered). The deposit goes to the owner, so the records do not change and an owner with
no PAC can still close its balance; a sponsor counts it as the cost of bringing in a user.

**A refundable deposit and a free list, so that unused balances are reused.** The XRP Ledger, Stellar and Algorand (to
the knowledge of the author) lock a reserve that the holder gets back when it closes its line, and
[PIP-50](./pip-50.md) locks a deposit for an anchor that its owner gets back when it deletes it. A deposit bounds what
is in use by the PAC that people accept to lock, instead of by what was ever created. The tree of Pactus only appends,
so a closed balance is not cut out: its record becomes a free slot on a stack, the next balance reuses it, and no
index moves. A node never has to shrink the tree or move a record. The tree keeps the length of its peak, with free
slots of 5 bytes in place of the closed balances, and since a slot is appended only when none is free, the deposits
bound the length of the tree as well as the balances in use. The deposit is refunded as it was posted, so a change of
the constant never touches an existing record, and the fee is taken from the refund so that nobody is stuck with all
its PAC locked. Asset records are the exception: they are permanent, since every holding points to one, and they are
paid for once, which is why `AssetCharge` is not small. Their cost is also what an attacker pays to make the permanent
part of the state grow, which is the only part of the state that the deposits do not bound.

**Charges known from the payload.** `Value()` is computed from the payload and the constants of section 1, so a wallet
never has to guess a fee from the state, and no fee code depends on the state. Because, in this PIP, only creation and
acceptance place records, and which records they place follows from the payload, each charge or deposit is for a
record that is in fact placed.

**Separate domains in the asset tree.** The leaves and inner nodes of the asset tree are tagged, with the tags of
Certificate Transparency (RFC 6962), and a leaf commits to its index. The trees of accounts and validators need
neither: every record there carries its own number, so no two leaves are equal, and the hash of a block commits to the
number of its transactions next to their root. An asset record carries no number and two of them can be equal, so the
index goes into the leaf. With it the asset root commits to every record and to their number, and with the tags no
rule on the length of a record is needed, in this PIP or a later one. The shape of the tree stays that of the node, so
the change is a tag in the hash of an inner node and a few bytes in the hash of a leaf.

**Room for pools, but no pools.** Exchanges are where token chains lose the most: price manipulation, sandwiches,
inflated first shares, honeypots. They deserve a PIP of their own, reviewed on its own. This PIP only reserves what
such a PIP needs (section 6): kinds of record, a header that can grow, the `AssetID` 0 for PAC, assets without an
issuer for the shares of a pool, and the rule that every payload of the asset layer counts under the same cap. These
reservations cost no byte and no rule today, and a pool PIP then changes nothing in the records, payloads or
invariants of this one.

**PAC pays everything.** There is no second fee token. A new holder needs a little PAC for the deposit and the fee to
accept an asset, unless a sponsor pays them (section 3.9), and for the fee to move it.

## Alternatives Considered

1. **Off-chain execution checkpointed by a bonded committee** (an earlier draft of this PIP). Rejected as too complex
   and for its trust assumptions. It remains a possible later PIP if asset demand outgrows the cap.
2. **A profile over [PIP-50](./pip-50.md) anchors, computed by indexers.** No consensus change, but Pactus enforces
   nothing: validity is whatever the indexer says.
3. **A smart-contract VM.** Attack surface out of proportion to the tokens this PIP targets.
4. **Item records inside an asset (collections).** Set aside: more state and rules, and the single record covers the
   need at the cost of more creations.
5. **Shrinking the tree when a balance is closed**, by moving the last record into the hole and dropping the last
   leaf. It would give the space back for real, but it needs a tree that can drop its last leaf, which the trees of
   the node do not do (their width only grows), and a second tree so that an `AssetID` never moves. The free list
   bounds the records in use, and the length of the tree through its peak, with the tree that exists.
6. **Fees in the assets themselves.** No common unit, and no way for a new holder to pay a first fee. The rates of
   section 3.3 are not fees of this kind: they are a property of the asset that its issuer chose, and they do not pay
   for the transaction.
7. **The node merges transfers of different senders into one transaction with many senders.** Not possible with
   account signatures, which cover one payload each. Bundles of whole signed transactions are possible (the next
   alternative).
8. **Bundles in this version.** The proposer packs the asset transactions of any senders into bundles of up to 8, each
   of them one entry of the block: either an unsigned transaction built like the subsidy transaction, whose ID covers
   the IDs of its items, or a new kind of entry in the body of a block, which changes the format of a block, its
   decoder and its transaction root. Both save entries and not work, and both are new to every part of the node that
   reads a block. Set aside for this version, whose cap leaves PAC 90 % of every block, and kept as an extension
   (Future Extensions).
9. **Rates that are fixed, or that have no bounds.** Fixed rates are possible (`Min == Max`) but not the only choice.
   Unbounded rates would let an issuer take any share of any transfer.
10. **The sender pays for the recipient's record, with no opt-in** (to the knowledge of the author, the model of
    Cardano and Solana, with a refundable reserve in each). Simpler to use, but anyone can put an asset in any wallet,
    and the recipient has no say in the record that is created for it. Set aside for the opt-in of section 3.7.
11. **Higher charges and wallets that hide unknown assets.** No consensus change, but it prices spam instead of
    stopping it, and the records stay in the state. It remains a rule for wallets in any case.
12. **Balances that are never closed, paid for once.** The simplest rule, but the state only grows and its owners get
    nothing back, which is weaker than the reserves of the chains above.
13. **A sponsored acceptance whose deposit returns to the sponsor.** Fairer to the sponsor, but each holding must name
    its payer (67 bytes instead of 46), and an owner with no PAC could no longer close its balance, since the fee of
    the close is paid from the refund.
14. **A second signer that pays the fee of any transaction,** as some chains have. It would help every payload, but it
    changes every transaction of Pactus, not only the asset layer.
15. **A set of used acceptances** that nodes keep from the recent blocks, as they keep the IDs of recent transactions.
    No byte in the state and no delay before a close, but the validity of a block would depend on history that the
    state root does not cover, which every restart, snapshot and sync would have to rebuild exactly. The `LockedUntil`
    of section 3.9 gives the same guarantee from the state alone.

## Backwards Compatibility

This is a consensus upgrade. Nodes that do not implement version `V` reject payload types 8 to 14 and cannot compute
the extended state root. Existing payload types, account records and validator records keep their encoding. Accounts
that never use the feature are unaffected.

Activation follows [PIP-51](./pip-51.md): implementations advertise version `V`; when more than 75 % of committee
power supports it, proposers raise the block version; from the first block of version `V` the extended root applies,
the asset tree exists with its header record, and the seven types are legal. Before that block they are invalid: rule
1 of section 4.1, which reads the version in the header of a block, makes a block that carries one invalid, pools
reject them, and the asset tree does not exist. The activation cannot be undone, and the node already guarantees it:
when it commits a block of a higher version, it raises the lowest version that it accepts to that version, restores it
from the last block after a restart, and from then on rejects any block of a lower version and proposes that version
or higher. Once a block of version `V` is committed, a block of a lower version is therefore invalid, and the
existence of the asset tree says the same in the state. The format of a block does not change; software that decodes
the transactions of a block (explorers, indexers, wallets) must learn the seven payloads. State sync and snapshots
MUST carry the asset tree from then on. Testnet activates first, and mainnet only after the testnet plan of the
Reference Implementation section has passed.

## Test Cases

Implementations MUST pass at least these. They add no rule to the Specification.

* **Activation and root.** The seven payload types are rejected below `V`, in a block and in a pool. After the first
  block of `V`, a block of a lower version is invalid, even after a restart or when the support of the committee
  falls. The first block of `V` has the extended root, with an asset tree that holds only the header (`FreeHead` at
  `NoRecord`, `DepositTotal` 0), whose root is therefore `leaf(0)` of section 2.1. The root changes when a record
  changes, and a restart reloads the same root.
* **Create.** A fixed asset, a minting asset and an asset with `InitialSupply == 0` are created. Rejected: an empty
  symbol, 13 bytes, lowercase, a symbol of `PAC`, `Decimals` 10, `MaxSupply` 0 or above `MaxAssetSupply`,
  `InitialSupply` above `MaxSupply`, insufficient PAC, a treasury or validator `From`. `AssetCharge` reaches the
  treasury and is never returned. The creator's holding is placed, with a deposit that raises `DepositTotal`, only if
  `InitialSupply > 0` or the policy names the creator as collector. The asset record is always appended at the end,
  even when there is a free slot. With a policy, rejected: `Current` outside `[Min, Max]`, a `Max` above 10 000,
  `TeamRate.Max + BurnRate.Max` above 10 000, all `Max` at 0, `TeamCap` of 0, a treasury or validator `Collector`, and
  a `Collector` other than `From` with a `TeamRate.Current` above 0, or a `TeamRate.Min` above 0. With a policy that
  names the creator as collector, the creator's holding exists right after creation, at balance 0 if `InitialSupply`
  is 0, and is placed once. With a policy that names another account as collector, no record is placed for that
  account, its PAC balance is unchanged, and the asset can be transferred at once, with no team share.
* **Accept.** An account accepts an asset: a holding with balance 0 is placed, `HoldingDeposit` leaves its PAC balance
  and raises `DepositTotal`, nothing reaches the treasury, and the account can then receive. With no free slot the
  record is appended at the next index; with one, it takes the slot at `FreeHead`. Rejected: an unknown asset, a
  second `AssetAccept` of the same asset by the same account (nothing is locked twice), insufficient PAC, a treasury
  or validator `From`. A creator that holds a record from creation (an initial supply, or itself as collector) cannot
  accept again. An accept and a transfer to that account in one block, in that order, both succeed; in the other order
  the transfer makes the block invalid. A collector other than the creator that accepts lets the issuer raise the team
  rate.
* **Sponsored acceptance.** A sponsor opens a holding for an account with 0 PAC: the PAC of the sponsor falls by the
  deposit and the fee, `DepositTotal` rises by the deposit, and the PAC of the owner does not change. The owner can
  then receive, and closes the holding with 0 PAC, getting the deposit back less the fee. Rejected: an
  `OwnerSignature` that does not verify, an `OwnerPublicKey` that is not the key of `Owner`, an acceptance signed for
  another asset, another owner, another `Expiry` or another network, an expired acceptance, an `Expiry` more than
  `TransactionToLiveInterval` blocks after the block, `Owner` equal to `From`, a treasury or validator `Owner`, an
  owner that already holds the asset, and a sponsor without enough PAC. The signature of a transaction does not verify
  as an acceptance, and an acceptance does not verify as a transaction. The holding that an acceptance opens has its
  `Expiry` as `LockedUntil`, and the boundary is exact: for an acceptance with `Expiry = H` included at height `H`, an
  `AssetClose` of the holding at `H` is rejected and at `H + 1` is valid, and an `AssetAcceptFor` that carries the
  same acceptance at `H + 1` is rejected as expired. An acceptance opens at most one holding: a second
  `AssetAcceptFor` with the same acceptance fails in the same block (an `AssetAcceptFor`, an `AssetClose` that is
  rejected, then the same acceptance again) and in every later block, with another valid signature of the same message
  too, and the same holds after a restart of the node, a start from a snapshot or a sync. An acceptance whose
  `AssetAcceptFor` was rejected before inclusion, for example because the owner already held the asset, can still open
  a holding before its expiry, and once the holding is closed, a new acceptance with a later `Expiry` opens a holding
  again.
* **Close and free slots.** An owner closes its holding: its PAC balance rises by the `Deposit` posted in the record,
  less the fee, `DepositTotal` falls by the same `Deposit`, and the record becomes a `FreeRecord` that is the new
  `FreeHead`. With `MaxBurn` at 0 the balance must be 0. With a `MaxBurn` at least the balance, the units are added to
  `Burned`, no rate applies, and the sum of the holdings still equals `Issued - Burned`. Rejected: an unknown asset,
  an account with no holding, a balance above `MaxBurn` (even by one unit), another account's holding, a holding with
  `h <= LockedUntil`, the collector while `TeamRate.Current` is above 0, a `MaxBurn` above `MaxAssetSupply`, and a
  close that would take the PAC balance above `MaxNanoPAC`. At the PAC bounds: with `PAC(From) = MaxNanoPAC`, a close
  with `Deposit = fee` is valid and one with `Deposit > fee` is rejected; with `fee > Deposit`, a close is rejected at
  `PAC(From) = 0` and valid at `PAC(From) = fee - Deposit`, which leaves 0. An account with 0 PAC and a deposit that
  covers the fee can close. A holding placed by `AssetCreate` or `AssetAccept` has a `LockedUntil` of 0 and can be
  closed at once. After two closes, two accepts take the slots in the reverse order of the closes, the tree grows by
  no record, and `FreeHead` ends at `NoRecord`. A `HoldingDeposit` that a later version changes does not alter the
  refund of an old record. A closed account that accepts again gets a record that is unrelated to the old one. Units
  sent to an owner after it signed a close with `MaxBurn` at 0 make that close fail and cost the owner only the new
  signature; the same close with a `MaxBurn` above the dust goes through and burns it.
* **Transfer.** One recipient and eight succeed; nine fail. Rejected: a repeated `To`, `To == From`, a validator
  recipient, an amount of 0 or below, a `MaxRate` above 10 000, an unknown asset, a balance that is too small, a
  recipient that has not accepted the asset, and 8 recipients of `2^62` each (the overflow case of PIP-54), which
  fails before any addition. An asset whose collector has not accepted it, at a team rate of 0, accepts transfers and
  pays no team share. A transfer to the zero address needs no holding, raises `Burned` and creates no record. A
  holding that reaches zero stays. `Value()` is 0, and the number of records of the tree is the same before and after
  any transfer.
* **Rates.** The example of section 3.3 gives `team = 15 000`, `burn = 5 000` and `net = 980 000`. With the same rates,
  99 gives `team = 1`, `burn = 0`, `net = 98`, and 49 gives `team = burn = 0`. A transfer of `2^63 - 1` with rates
  of 10 000 in total is computed without leaving the `int64` range, and `team + burn + net` equals `Amount` for a
  range of amounts and rates, including values just below and above multiples of 10 000. `TeamCap` limits `team` and
  not `burn`. An entry whose `net` is 0 is rejected. `MaxRate` below the current sum of the rates fails the transfer,
  and an asset without a policy accepts `MaxRate` 0. An entry to the zero address pays no rate. The recipient, the
  collector and `Burned` change as specified when the collector is the recipient or the sender.
* **Set rate.** The issuer sets a rate inside its bounds and the next transfer uses it. A value outside `[Min, Max]`,
  a non-issuer, an asset without a policy and an unknown asset fail. An asset with `Min == Max` accepts only that
  value. Bounds, cap and collector never change. With a collector other than the issuer, raising `TeamRate` above 0
  fails until the collector accepts, and succeeds after. The collector cannot close its balance while
  `TeamRate.Current` is above 0; after it closes at a rate of 0, raising the rate fails again until it accepts again.
  A team rate of 0 is accepted whatever the state of the collector, and an issuer that is its own collector sets any
  rate within the bounds. After every step, a `TeamRate.Current` above 0 has a collector that holds the asset (section
  2.3).
* **Mint.** Only the issuer mints. A mint above `MaxSupply - Issued` fails. After a burn, a mint still cannot pass
  `MaxSupply` in total. An asset with `MaxSupply == InitialSupply` rejects every mint. A mint to an account that has
  not accepted the asset fails, including a mint by an issuer to itself when `InitialSupply` was 0 and it holds no
  record. A mint places no record and has `Value()` 0.
* **Block cap.** A block with 100 asset transactions and 899 other transactions is valid; a block with 101 asset
  transactions is invalid, and it is rejected before the signature of any transaction is verified. An asset
  transaction in a block below `V` makes it invalid. Two asset transactions of one sender in one block run in order,
  and an asset transaction with a bad signature, an expired lock time, an ID that was already executed or a balance
  that is too small makes the block invalid. A proposer with more asset transactions in its pool than the cap includes
  `MaxAssetTxPerBlock` of those that pass their checks.
* **Invariants.** The invariants of section 2.3 hold after every test, free list and collector included. Balances,
  stake, treasury and `DepositTotal` sum to the PAC supply after every test: asset transactions only move PAC to the
  treasury, lock it in a deposit or give it back, and pay the fee.
* **Determinism.** Two nodes with different local indexes and one restarted from a pruned store obtain the same root
  and the same `GetAsset`. A tree rebuilt from the store, in the order of the store, has the same root as the tree
  built block by block, for small trees and for a tree of at least 50 million records. Every payload decodes and
  re-encodes to the same bytes, and trailing bytes are rejected.
* **Hostile inputs.** Invalid: a varint that is longer than its shortest encoding, 9 recipients, a symbol length of
  13, each rejected before any allocation of that size. A block that repeats a transaction ID is invalid, and so is a
  transaction executed in an earlier block and included again. A signature made for a PAC transaction does not
  validate an asset payload. A node whose local index disagrees with the tree stops. A rate raised in the pool after a
  transfer was signed with a tight `MaxRate` makes that transfer fail, and does not charge more. Two `AssetSetRate`
  included in the opposite order of their signing leave the rates of the later inclusion. An `AssetAccept` and a
  transfer to the account that signed it, skipped in the first pass of a proposer, are included in the same block
  after a second pass. Records with the same bytes give different leaves: a tree of 5 records and a tree of 8 records
  that adds three copies of its last record, an `AssetRecord`, have different roots, and so do trees of n and n + 1
  records that end with copies of one record. An `Expiry` of `2^32 - 1` is compared without overflow, and rejected
  while it is more than `TransactionToLiveInterval` blocks ahead. An asset transaction whose `From` is the treasury
  address is rejected by `BasicCheck` without a signature, by the pool, and in a block, and the balance of the
  treasury does not change.
* **Room for later PIPs.** Every payload that names an asset rejects an `AssetID` of 0 in `BasicCheck`. No
  `AssetCreate` gives an asset the zero address as `Issuer`, and `AssetMint` and `AssetSetRate` never pass with the
  treasury as `From`. No payload of this PIP creates a record of kind 4 or more. The header has 13 bytes, and the
  conservation of section 2.3 counts every PAC total of the header.

## Reference Implementation

None yet. Before this PIP leaves Draft, a pull request will add the seven payloads, the asset tree, the extended root,
the block cap and the RPC to the Pactus node, and report on stated hardware: the time to validate a block with
`MaxAssetTxPerBlock` asset transactions of 8 recipients each, and with as many `AssetAcceptFor`, for BLS, Ed25519 and
secp256k1 keys, which is what sets the cap; the cost of a tree update, the size of the store per record, and the
effect on state sync.

### Testnet plan before mainnet

This PIP SHOULD NOT activate on mainnet before its reference implementation has run on testnet through the steps
below, with the results published. Each step tests a failure, not only the path where everything works.

1. **Load.** Blocks at the cap: 100 `AssetTransfer` with 8 recipients each, for BLS, Ed25519 and secp256k1 senders,
   and the other 899 entries filled with `BatchTransfer`; and blocks with 100 `AssetAcceptFor`, which verify two
   signatures each. The time to validate and to commit them, on the smallest hardware that validators are expected to
   run, sets `MaxAssetTxPerBlock` with a wide margin under the block interval.
2. **Restarts and snapshots.** Nodes restarted at random, nodes started from a snapshot and nodes synced from the
   first block keep the state root of the others at every height and, like them, reject the reuse of an acceptance,
   before and after a restart or a snapshot; a dedicated test does the same with an asset tree of at least 50 million
   records (Test Cases).
3. **Activation.** The switch to version `V` under [PIP-51](./pip-51.md), with and without enough support, and the
   floor of the block version: after the first block of `V`, no block of a lower version is accepted, even after a
   restart.
4. **Hostile proposers and peers.** Blocks with 101 or 999 asset transactions, asset transactions below `V`, repeated
   transaction IDs, the reuse of an acceptance, or asset transactions signed by the treasury are rejected, and
   rejecting a block over the cap costs no more than reading it.
5. **Pools under flood.** A flood of asset transactions that are valid alone and invalid together, with the
   per-sender limit on: payments keep flowing, and the asset lane recovers when the flood stops.
6. **State over time.** Weeks of mixed traffic, with accepts, closes and creations at the cap: the size of the store,
   the length of the tree and `DepositTotal` stay within the bounds of Security Considerations, and the invariants of
   section 2.3 hold at every block.
7. **Wallets and explorers.** The RPC of section 5 and the wallets show deposits as locked PAC, the net amount of a
   transfer with rates, the bounds of the rates, whether a collector has accepted, and the units that a close burns. A
   wallet signs an acceptance only after showing its asset, its issuer, its expiry, which is short by default, and
   that the holding cannot be closed before that expiry.

### Open items of this draft

* **A reference implementation.** No part of this PIP has run inside a Pactus node.
* **Byte-level vectors** for each payload, for the leaves, inner nodes and root of the asset tree, and for the
  extended root.
* **Constants.** Every value of section 1 is an initial proposal, not measured. `MaxAssetTxPerBlock` is set by the
  benchmark of the Reference Implementation.
* **The testnet plan.** None of it has run, and mainnet waits for it.

## Security Considerations

### Arithmetic

[PIP-54](./pip-54.md) came from a sum that wrapped. Every quantity here is an `int64` bounded by `MaxAssetSupply`,
every sum is checked before it is added, and the invariants of section 2.3 are checked in tests. A credit cannot
overflow, because a balance never exceeds the supply of its asset. The test with 8 recipients of `2^62` is mandatory.
The same care applies to PAC: `Value() + fee` and every balance are bounded by `MaxNanoPAC` before the sum.
`AssetClose`, the one payload that gives PAC back, applies the difference between its deposit and its fee in a single
direction, with no intermediate sum (section 3.8), and no rule adds two heights (section 3.9).

### State growth

In this PIP, the state has two parts, and they are bounded differently.

**Balances in use are bounded by the PAC locked for them.** A holding exists only while a deposit of `HoldingDeposit`,
posted by its owner or by a sponsor, stays locked for it, and closing it returns the deposit to the owner and frees
the slot, so the number of holdings in use is at most the locked PAC divided by the deposit: with 42 million PAC, at
most 420 million records of 46 bytes, about 19.3 GB, and only if every coin were locked. The deposit is about 2.2 mPAC
per byte, the same order as the anchor of [PIP-50](./pip-50.md) (about 4.5) and a validator record (about 8.3).
Transfers and mints never grow the state, and nobody can make an account hold, or pay for, a record that it did not
sign for.

**The length of the tree is bounded by the deposits too.** A holding is appended only when no slot is free, that is,
when every holding slot holds an open balance. The tree therefore never has more holding slots than the largest number
of balances that were open at the same time, each with its deposit locked at that moment, and the bound above holds
for the length of the tree as well as for the balances in use. Closing does not shorten the tree: the slots stay as
free records of 5 bytes until the next balances take them. To lengthen the tree for good, an attacker must keep a
deposit locked for every slot until the last one is open, and pay two fees per slot, one to open it and one to close
it. At the cap, 100 openings per block add 4.6 KB per block, about 40 MB a day, for 8 640 PAC a day in fees, with
86 400 PAC locked by the end of the day and returned afterwards. The opening fee alone is 2.1 times the price per
byte, and 8 times the price per record, of the accounts that `BatchTransfer` creates today (0.01 PAC for 8 accounts of
12 bytes), which Pactus already accepts with no deposit at all.

**Asset records are permanent, and they are paid for.** A sender that fills the cap with `AssetCreate` and no initial
supply adds 13.4 KB per block, about 864 000 records and 116 MB a day, and spends about 95 000 PAC a day on
`AssetCharge` and fees; one gigabyte of asset records costs about 820 000 PAC. Today a sender can create up to 8 000
accounts per 1 000-transaction block with `BatchTransfer`, about 830 MB a day, so the permanent part is bounded below
what Pactus already accepts for accounts. Together, the two parts stay far below the 2^31 records that the tree can
hold (section 2.1): at most 420 million balances, and asset records that cost `AssetCharge` each, so that 2^31 of them
would cost about 215 million PAC, five times the supply. `AssetCharge`, `HoldingDeposit` and the cap are constants
that a later version can change.

A proposer is the one attacker that the fee cannot price out. The fixed fee is a rule of the pools, not of consensus,
which accepts any fee from 0 to `MaxNanoPAC`, and the fees of a block go to its proposer, or to the owner of its
stake. A proposer therefore pays no fee, in net, for the asset transactions that it puts in its own blocks, as it pays
none today for its own `BatchTransfer`. It still pays `AssetCharge` for every asset, which goes to the treasury and
never back to it, it still locks a deposit for every balance, and it still cannot exceed `MaxAssetTxPerBlock` per
block, so the bounds above hold for a proposer too; only the figures in fees drop, and only in its own blocks.

An account that accepts an asset by mistake closes the balance and gets its deposit back, less a fee, once the
acceptance has expired if a sponsor opened it. It cannot refuse units that a holder sends it, but a close with a
`MaxBurn` above those units goes through anyway, so dust cannot keep an owner from recovering its deposit; the sender
of the dust loses the units, and the owner loses nothing.

### Block capacity

The cap keeps assets to at most `MaxAssetTxPerBlock` entries of a block, 100 of its 1 000 (section 4.1), so PAC keeps
at least 90 % of them, whatever the demand for assets. The same number bounds the **work** of assets, and it must come
from the benchmark: an `AssetAcceptFor` verifies two signatures, so the worst block verifies 1 099 signatures instead
of 999. A spammer who fills the asset lane (100 transactions, 1 PAC a block at the fixed fee of the pools) delays
other asset users; it takes no entry from PAC, and the work and the state that it adds to a block stay within the
bounds of `MaxAssetTxPerBlock`. A validator counts the asset transactions of a block before it verifies any signature,
so a block over the cap costs it no more than reading it. Pools are local policy, and the separate asset pool keeps
asset transactions from filling the memory of a node at the expense of payments.

### The issuer

A minting asset gives its issuer the power to create units up to `MaxSupply`. A wallet MUST show whether an asset is
minting and how much room is left, before the user buys it. The issuer key cannot be replaced: if it is lost, no more
units are minted and the rates stay where they were; if it is stolen, the thief can mint up to the cap and move the
rates inside their bounds. An asset with `MaxSupply == InitialSupply` and fixed rates has no such risk. Nobody can
freeze, claw back or change the metadata of an asset.

### Transfer rates

An issuer with a variable rate can move it to its `Max` at any time, and a `Max` of 100 % is a trap: the asset can be
sold while the rate is low and then turned into one that keeps every transfer. The bounds are public and can never be
widened, so the damage is limited to what they say, but only if the user reads them. A wallet MUST show the `Max`
rates, and whether a rate is variable, before the user buys the asset, SHOULD warn when the two `Max` rates are high,
and MUST set `MaxRate` on every transfer it builds to the rate it showed, never to the `Max` of the asset unless the
user asks for it. A rate change that lands between signing and inclusion cannot take more than `MaxRate`. A collector
that is the issuer, or a key that the issuer controls, receives the team share without any further rule, so users
judge the asset by the issuer, not by the symbol. The shares round down, so many small transfers can avoid a rate;
this costs the issuer revenue and nobody else anything. A transfer rate does not apply to a mint or to a burn. A later
PIP for exchanges or pools follows section 6 on rates.

The collector of an asset can never be changed. A collector other than the issuer starts at a team rate of 0, and the
rate rises only once it has accepted the asset (section 3.6), so a collector that cannot accept, for instance a
mistyped address, never blocks the asset: its issuer only never receives a team share. A wallet MUST have the issuer
confirm the collector address before it signs an `AssetCreate` with a policy, and SHOULD show whether the collector of
an asset has accepted it. The acceptance of a collector can be sponsored by the issuer (section 3.9).

### Identity and spoofing

Symbols are not unique and anyone can create one, such as `USDT`. Opt-in stops an asset from being pushed into a
wallet, but a user can still accept a look-alike by following a link or a QR code. A wallet MUST show the `AssetID`
and the issuer address and not only the symbol, MUST NOT trust a symbol, and MUST ask for confirmation, with those two
values, before it signs an `AssetAccept` or an acceptance. The symbol `PAC` is reserved so that no asset looks like
the coin. An `AssetID` in a link is a request and not an authorization: nothing happens until the user signs. Symbols
can also mislead by their digits (`0` and `O`, `1` and `I`), and so can `Decimals`: two assets with one symbol, one
with 9 decimals and one with none, show quantities that differ by a factor of a billion. A wallet shows the decimals,
and amounts in the units of the asset that it reads from the state.

### Hostile inputs and what the user signs

* **An `AssetID` is known only after inclusion.** It is the position of the record in the tree, assigned when
  `AssetCreate` executes. Another creation can land first, so a wallet MUST NOT announce, accept or send an `AssetID`
  that it has not read from an included `AssetCreate`. Otherwise someone who sees a pending creation can take the ID,
  give it the same symbol, and have the announced ID accepted.
* **Metadata is attacker-chosen.** The document behind `MetaHash` can say anything. Wallets and explorers MUST check
  the hash before they use it, cap its size, accept only fixed content types, run no active content from it, and
  fetch no address that it embeds without the user asking.
* **Blind signing.** A wallet MUST show the decoded payload before it signs: the type, the `AssetID`, the symbol, the
  issuer, each recipient with its gross and net amount, the rates and `MaxRate`, and for a close the units that it
  burns. It MUST NOT sign a payload that it cannot decode, and a signing device that cannot show these values SHOULD
  refuse asset payloads.
* **Pool flooding.** Funded accounts can flood the asset pool with transactions that are valid alone and invalid
  together. The per-sender limit and the cost-ordered checks of section 5 bound this; the pool is local policy, so a
  node that does not apply them loses its own memory and nothing else.
* **Signed acceptances.** An acceptance only lets its owner receive: it is not a permit, and it never authorizes a
  transfer or the spending of anything. A user tricked into signing one gets, at worst, a holding that it did not
  want, paid for by someone else, which it can close, once the acceptance has expired, to keep the deposit; the
  acceptance never opens it again (section 3.9). A wallet MUST show the `AssetID`, the issuer and the expiry before it
  signs an acceptance, as for an `AssetAccept`, MUST say that the holding that the acceptance opens cannot be closed
  up to that expiry, and MUST build the bytes that it signs itself, never sign bytes that an application hands it.
* **Index corruption.** A local index that disagrees with the tree is a consensus fault, not a cache miss, which is
  why section 5 makes a node stop.
* **The treasury as signer.** The node takes any transaction whose signer is the treasury address for the subsidy
  transaction, which carries no signature and no fee, and its `IsAccountAddress()` accepts the treasury address. An
  asset payload that let the treasury be `From` would need no signature: anyone could lock the PAC of the treasury in
  deposits, or act as the issuer of an asset created in its name. Hence the explicit rejection of section 3.1.

### Keys, replay and burns

Assets use ordinary accounts. Replay protection is that of every transaction: the lock time, and the rejection of a
transaction ID that was already executed. An acceptance is protected by its expiry and by the holding that it opens,
whose `LockedUntil` keeps it open until that expiry (section 3.9). There is no allowance, so a signature can never
authorize someone else to spend later. A transfer to the zero address destroys units for good, and a wallet SHOULD ask
for confirmation. Loss of a key is the loss of its holdings, as for PAC.

### Privacy

Balances and transfers are public, as for PAC. This PIP adds no privacy.

## Future Extensions (informative)

* **Collections.** A token-ID dimension if one asset per item proves too costly.
* **A separate rate controller,** for example a multi-signature or a vote, and a delay before a new rate applies.
* **Removal of assets that nobody holds,** which needs a count of the holdings of each asset, to bound the permanent
  part of the state too.
* **Exchanges,** in dedicated PIPs that use the room of section 6: an atomic swap, so that two parties can exchange
  assets or an asset and PAC in one transaction, and liquidity pools with a constant product, in the style of
  PancakeSwap v2.
* **Bundles,** if asset traffic stays at `MaxAssetTxPerBlock`: the proposer packs the asset transactions of any
  senders into bundles of up to 8, each of them one entry of the block, so that the cap on work can rise without
  taking more entries from PAC. The design worked out for this PIP: a bundle is an unsigned transaction built like the
  subsidy transaction, so the format of a block does not change; its ID covers the IDs of its items and not their
  bytes, because the store strips the public keys that it already knows; at most one bundle of a block is partial, so
  a proposer cannot waste entries; the counts are checked before any signature; and a bundle never holds another
  bundle. It needs a prototype in the node first, and a comparison with a new kind of entry in the body of a block.
* **An off-chain layer** with its own accountability, if asset demand outgrows `MaxAssetTxPerBlock`, even with
  bundles.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
