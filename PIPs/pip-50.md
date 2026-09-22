---
pip: 50
title: Native State Anchoring (Pruning-Resistant Live State Slot)
description: Live per-account commitment slot, timestamps, and node APIs.
author: Johan (@johan256x)
status: Draft
type: Standards Track
category: Core
created: 2026-03-11
updated: 2026-09-16
requires: 51, 54
---

## Abstract

This PIP adds a single **live state slot** to each Pactus account. The slot is the whole
on-chain contract an off-chain application needs:

* a bounded digest (`RootHash`);
* an optional pointer to off-chain bytes (`ManifestURI`);
* a type hint (`AnchorType`);
* a refundable lock (`LockedDeposit`);
* protocol-written **create** and **update** timestamps (height + Unix time).

The slot lives in **current global state**. A pruned node can serve it without historical
transactions. Delete refunds the deposit and the attestation is no longer active.

Node implementations MUST also expose read, build-tx, and change-notification APIs so
wallets, indexers, and apps (Stamp, DID, tickets, manifests) do not invent a parallel
convention. Consensus still does not store files, search, or Merkle paths of user data.

Activation is protocol version **5** via [PIP-51](./pip-51.md).

## Motivation

Pactus has no smart-contract execution layer. Applications that need a **current**
commitment (revocation roots, DID documents, ticket registries, document integrity)
today have only memos, extra accounts, or off-chain indexers.

That is not equivalent to a live state slot:

| Mechanism | Survives pruning | Current vs historical | Bounded | Can be revoked |
| --- | --- | --- | --- | --- |
| Tx memo (64 bytes) | No | Historical only | Per tx, unbounded history | No (history is immutable) |
| Extra dedicated account | Yes (balance only) | No commitment field | 12-byte account | No digest to revoke |
| Off-chain indexer | Depends on the indexer | Depends on the indexer | Unbounded | Trusts the indexer |
| **State Anchor** | **Yes** | **Current state** | **1 slot / account** | **Yes (delete)** |

A memo answers "this digest appeared in some past transaction."
An anchor answers "this account **currently** attests to this digest."

Those are different protocol questions. The second one cannot be answered from a pruned
node using memos, and cannot be answered trustlessly from an indexer. That is an
**on-chain** problem: Pactus already prunes ([docs](https://docs.pactus.org)), and the
global state root is the only object every full node is required to keep consistent.

Pactus's design principle (see discussion on PIP-48) is that off-chain problems should
have off-chain solutions. This PIP accepts that principle and claims a narrow exception:
**canonical live validity of a bounded digest is a state-root problem**, not an indexing
problem. Everything else (file storage, search, JSON-LD, ticketing logic) stays off-chain.

## Goals

* One optional slot per account, included in the existing account Merkle tree.
* Deterministic binary encoding, in the same style as existing payloads.
* Deposit-backed create; explicit delete refunds the deposit.
* Amount arithmetic that cannot overflow (`int64` / `MaxNanoPAC`), per PIP-54.
* **Pruning-resistant timestamps** written by the executor from the including block,
  never from the payload (the user cannot forge "I anchored in 2019").
* **A complete off-chain contract**: read APIs, unsigned-tx builders, and a change
  event so applications do not depend on archival tx bodies.
* An interoperable **application profile** (`PAC-ANCHOR-1`) for hashing and for
  committing many off-chain items under one root. Nodes MUST NOT enforce that profile.
* No third Merkle tree, no new store prefix, no VM, no consensus secondary index.

## Non-Goals

* Storing application payloads on-chain.
* On-chain URI fetch, schema validation, or `AnchorType` behavior.
* Directories, full-text search, or name resolution inside consensus.
* Merkle proofs of the account leaf against `stateRoot` (apps trust `GetAccount` the
  same way they already trust a balance). That can be a later PIP.
* Replacing WASM / sandbox dApps / Tanour.
* Multiple native slots per account (Merkleize off-chain instead).

## Specification

### 1. Design choice: extend `Account`, do not add a parallel registry

The March 2026 draft described a separate `AnchorRegistry` map. That map is **not**
currently part of the state root. Today's state root is:

```text
stateRoot = HashMerkleBranches(accountMerkle.Root(), validatorMerkle.Root())
```

A LevelDB prefix that is not hashed into `accountMerkle` would let two nodes commit the
same block header with different anchors. That is unacceptable.

This PIP therefore stores the slot as an **optional suffix on the existing `Account`
object**, the same pattern [PIP-49](./pip-49.md) used for validator delegation.

* Logical registry: `address → optional AnchorData` (at most one).
* Physical storage: extra bytes on the account record (`store` prefix `0x05`).
* Consensus coverage: `Account.Hash()` already hashes `Account.Bytes()`, which already
  feeds `accountMerkle`. No change to the state-root formula.

Key size is a Pactus address: **21 bytes** (`crypto.AddressSize`), not 20.

```go
type accountData struct {
    Number  int32
    Balance amount.Amount

    // Optional live slot. Absent means no active anchor.
    Anchor *AnchorData
}

type AnchorData struct {
    RootHash        []byte         // 32..64 bytes
    ManifestURI     string         // 0..128 UTF-8 bytes
    AnchorType      uint8
    LockedDeposit   amount.Amount  // nano PAC, not spendable
    CreatedAtHeight types.Height   // first Set, never overwritten
    CreatedAtTime   uint32         // Unix seconds of that block
    UpdatedAtHeight types.Height   // last Set
    UpdatedAtTime   uint32         // Unix seconds of that block
}
```

`Balance` remains the **spendable** amount. `LockedDeposit` is not spendable and is not
part of `Balance`. Locking MUST NOT mint or burn PAC.

Supply invariant for an account:

```text
AccountValue = Balance + LockedDeposit
```

A create/update that locks `D` MUST:

1. reject if `D > MaxNanoPAC - fee` (and the same class of check for `Balance`);
2. subtract `D` from `Balance`;
3. add `D` to `LockedDeposit` without wrapping.

Explorers that audit supply MUST count `LockedDeposit`. Omitting it would look like a burn.

### 2. Account serialization (backward compatible)

Current accounts are a fixed **12-byte** record: `Number` (int32) + `Balance` (int64),
little-endian via `encoding.WriteElements`.

This PIP does **not** rewrite existing 12-byte records. Decoding:

1. Read `Number` and `Balance` (12 bytes). Always required.
2. If EOF: `Anchor == nil` (all current mainnet accounts).
3. If more bytes follow: read the optional suffix specified below.
4. Trailing bytes after a well-formed suffix MUST fail decoding.

Suffix when `Anchor != nil`:

| Field | Type | Size | Notes |
| --- | --- | --- | --- |
| `HasAnchor` | `uint8` | 1 | MUST be `1`. `0` is invalid in the suffix (omit the suffix instead). |
| `HashLen` | `uint8` | 1 | `32 <= HashLen <= 64` |
| `RootHash` | bytes | `HashLen` | Opaque commitment |
| `URILen` | `uint8` | 1 | `0 <= URILen <= 128` |
| `ManifestURI` | bytes | `URILen` | UTF-8, may be empty |
| `AnchorType` | `uint8` | 1 | Opaque to consensus |
| `LockedDeposit` | `int64` | 8 | Nano PAC, `0 < LockedDeposit <= MaxNanoPAC` |
| `CreatedAtHeight` | `uint32` | 4 | First Set. Executor-written. |
| `CreatedAtTime` | `uint32` | 4 | Unix time of that block. |
| `UpdatedAtHeight` | `uint32` | 4 | Last Set. Executor-written. |
| `UpdatedAtTime` | `uint32` | 4 | Unix time of that block. |

These four timestamp fields MUST NOT appear in the transaction payload. The user cannot
choose them. The executor copies them from the **including block**: `CurrentHeight()` and
the block header `UnixTime`. Implementations MUST thread that Unix time into the sandbox
(today `Sandbox` only exposes `CurrentHeight`; this PIP requires `CurrentUnixTime() uint32`
as well).

Maximum suffix size: `1+1+64+1+128+1+8+16 = 220` bytes.
Worst-case account record: `12 + 220 = 232` bytes.

Writing:

* If `Anchor == nil`, write exactly 12 bytes (identical to today).
* If `Anchor != nil`, write 12 bytes plus the suffix.
* Implementations MUST NOT write `HasAnchor = 0`.

`LockedDeposit` in the account record uses a fixed `int64`, matching `Balance`, not a
varint. The payload still uses `Amount.Encode` (varint), matching other transactions.

### 3. Protocol parameter

| Parameter | Value | Mutable |
| --- | --- | --- |
| `MinAnchorDeposit` | `1 PAC` (`1_000_000_000` nano PAC) | Only by a later PIP |

`1 PAC` equals the genesis `MinimumStake`. It is a protocol constant on version 5,
not a genesis JSON field (genesis is immutable). Nodes MUST use this exact value after
activation. Testnet uses the same constant.

If a later PIP changes `MinAnchorDeposit`:

* Decreases: the owner MAY delete and recreate to recover excess. This PIP does **not**
  add a "withdraw excess" action.
* Increases: existing anchors remain valid without topping up.

### 4. Payload type

```go
TypeAnchor = Type(7) // next free type after TypeBatchTransfer = 6
```

Fee: **not a free transaction**. Same fixed-fee path as Transfer / Bond / Withdraw
(currently `0.01 PAC` by default, node-configurable). Sortition and Unbond remain the
only zero-fee payload types.

`Signer()` is the account that owns the slot. Only **account addresses** are valid
(BLS, Ed25519, secp256k1). Treasury and validator addresses MUST be rejected.

```go
const (
    AnchorActionSet    uint8 = 0 // create or overwrite
    AnchorActionDelete uint8 = 1
)
```

Unknown `Action` values MUST fail `BasicCheck` / decode.

#### 4.1 `AnchorActionSet` encoding

| Field | Type | Size | Description |
| --- | --- | --- | --- |
| `From` | `Address` | 21 bytes | Slot owner and signer |
| `Action` | `uint8` | 1 | `0` |
| `HashLen` | `uint8` | 1 | `32..64` |
| `RootHash` | bytes | `HashLen` | Commitment |
| `URILen` | `uint8` | 1 | `0..128` |
| `ManifestURI` | bytes | `URILen` | UTF-8 |
| `AnchorType` | `uint8` | 1 | Client hint |
| `Deposit` | `Amount` | varint | Additional lock this transaction (`>= 0`) |

`Value()` MUST return `Deposit`.

`Deposit == 0` is allowed **only as an update** of an existing slot (executor check).
Creating a new slot with `Deposit == 0` MUST fail.

#### 4.2 `AnchorActionDelete` encoding

| Field | Type | Size | Description |
| --- | --- | --- | --- |
| `From` | `Address` | 21 bytes | Slot owner and signer |
| `Action` | `uint8` | 1 | `1` |

No hash, URI, type, or deposit fields follow. Decoders MUST NOT read further payload bytes.

`Value()` MUST return `0`.

### 5. `BasicCheck` (stateless)

All of the following MUST fail the transaction before pool / execution.

#### Common

1. `From` is an account address.
2. `Action` is `0` or `1`.
3. `Value() >= 0` and `Value() <= MaxNanoPAC` (already applied by `tx.BasicCheck`).
4. `Fee >= 0`, `Fee <= MaxNanoPAC`, and the transaction is not treated as free.

#### Set

1. `32 <= HashLen <= 64` and `len(RootHash) == HashLen`.
2. `URILen <= 128` and `len(ManifestURI) == URILen`.
3. `ManifestURI` is valid UTF-8 (empty is valid).
4. `Deposit >= 0` and `Deposit <= MaxNanoPAC`.

#### Delete

1. Payload contains only `From` and `Action`.

The protocol MUST NOT interpret `RootHash` or `AnchorType`. All-zero `RootHash` is legal.

### 6. Execution (stateful)

Let `acc` be `Sandbox.Account(From)`. If `acc == nil`, fail `AccountNotFound` (same as Transfer).

All amount combinations below MUST use saturating-reject checks in the PIP-54 style:

```go
if a > amount.MaxNanoPAC-b {
    return ErrAmountOverflow
}
```

Never add user-supplied `int64` amounts before this check.

#### 6.1 Set (`Action = 0`)

Let `D = payload.Deposit`.

1. If `D > MaxNanoPAC - fee`, fail overflow.
2. If `acc.Balance() < D + fee`, fail `ErrInsufficientFunds`.
3. Let `locked = acc.LockedDeposit()` (`0` if no anchor).
4. If `locked > MaxNanoPAC - D`, fail overflow.
5. Let `newLocked = locked + D`.
6. If `acc.Anchor == nil` and `newLocked < MinAnchorDeposit`, fail
   (`newLocked` would be `D`; create requires `D >= MinAnchorDeposit`).
7. If `acc.Anchor != nil` and `D == 0`, keep `locked` unchanged.
8. Subtract `D + fee` from `Balance`.
9. Set `LockedDeposit = newLocked`.
10. Overwrite `RootHash`, `ManifestURI`, `AnchorType` with payload values.
11. Let `h = sbx.CurrentHeight()` and `t = sbx.CurrentUnixTime()`.
12. If this is a create (`previous Anchor == nil`):
    `CreatedAtHeight = h`, `CreatedAtTime = t`.
    If this is an update: leave `CreatedAt*` unchanged.
13. Always set `UpdatedAtHeight = h`, `UpdatedAtTime = t`.
14. `UpdateAccount(From, acc)`.

Create and update are the same action. The three public fields are replaced entirely
(not merged). Timestamps are protocol data, not payload data.

#### 6.2 Delete (`Action = 1`)

1. If `acc.Anchor == nil`, MUST fail (`ErrAnchorNotFound`). Not a no-op.
2. Let `locked = acc.LockedDeposit()`.
3. If `locked < fee`, fail `ErrInsufficientFunds`.
   (Fee is paid from the refund so an account that locked its entire balance can still exit.)
4. Clear `Anchor` (`nil`).
5. `Balance = Balance + locked - fee`.
6. `UpdateAccount(From, acc)`.

After delete, the account record MUST be written as 12 bytes again.

#### 6.3 What execution does not do

* No committee / sortition / bonding checks (unlike Bond / Unbond).
* No `strict` vs non-strict difference: pool and block use the same rules.
* No change to Transfer, Bond, Unbond, Withdraw, Sortition, BatchTransfer.
* Spendable transfers still use `Balance` only. They MUST NOT spend `LockedDeposit`.
* Timestamps are not payload fields and MUST NOT be user-supplied.

### 7. Transaction pool

Implementations MUST give `TypeAnchor` its own pool, sized like Transfer
(the remaining share of `MaxSize` after reserved bond/unbond/withdraw/sortition/batch
pools). Fee estimation uses the same `fixedFee()` as Transfer.

### 8. `AnchorType` (non-consensus)

Consensus stores the byte and MUST NOT branch on it.

| Value | Meaning |
| --- | --- |
| `0x00` | Generic commitment / raw digest |
| `0x01` | Service manifest |
| `0x02` | DID document |
| `0x03` | Verifiable credential / revocation registry |
| `0x04`–`0xFE` | Reserved; clients MUST treat as unknown |
| `0xFF` | Private / encrypted / proprietary |

Wallets MAY warn on reserved values. They MUST NOT reject a valid transaction because of
`AnchorType`.

### 9. Node interface (mandatory for official node)

Consensus does not require RPC. **The official Pactus node MUST** expose the following
on every public RPC surface it already ships (gRPC, gRPC-gateway, JSON-RPC). HTML MAY
display the same fields on the account page. This is the contract off-chain apps use.

An anchor is **found** iff the account exists and `Anchor != nil`.
Historical Anchor transactions MUST NOT be treated as active.

#### 9.1 `AnchorInfo`

```protobuf
message AnchorInfo {
  bytes  root_hash         = 1; // hex in JSON-RPC
  string manifest_uri      = 2;
  uint32 anchor_type       = 3;
  int64  locked_deposit    = 4; // nano PAC
  uint32 created_at_height = 5;
  uint32 created_at_time   = 6; // Unix seconds
  uint32 updated_at_height = 7;
  uint32 updated_at_time   = 8; // Unix seconds
}
```

`GetAccount` MUST include `optional AnchorInfo anchor = 6;` (unset = no active slot).
Apps MAY use `GetAccount` alone. `GetAnchor` is the dedicated shortcut.

#### 9.2 Read

```protobuf
rpc GetAnchor(GetAnchorRequest) returns (GetAnchorResponse);

message GetAnchorRequest  { string address = 1; }
message GetAnchorResponse {
  bool        found  = 1;
  string      address = 2;
  AnchorInfo  anchor = 3; // set only if found
}

rpc ListAnchors(ListAnchorsRequest) returns (ListAnchorsResponse);

message ListAnchorsRequest {
  uint32 skip  = 1; // number of matching accounts to skip
  uint32 count = 2; // 1..100, default 20
}
message ListAnchorsResponse {
  repeated AnchorListItem items = 1;
  uint32 total = 2; // accounts that currently have an anchor
}
message AnchorListItem {
  string     address = 1;
  AnchorInfo anchor  = 2;
}
```

`ListAnchors` walks current state (`IterateAccounts`), skips accounts with `Anchor == nil`,
and is **not** a consensus index. Order MUST be ascending `Account.Number` so pagination
is deterministic. This is enough for explorers and Stamp galleries without a third-party
indexer. Heavy filtering by `AnchorType` is an app concern; the node MAY ignore unknown
query fields.

#### 9.3 Build unsigned transaction

Follow the existing `GetRaw*Transaction` pattern:

```protobuf
rpc GetRawAnchorTransaction(GetRawAnchorTransactionRequest)
    returns (GetRawTransactionResponse);

message GetRawAnchorTransactionRequest {
  string from         = 1;
  uint32 action       = 2; // 0 = set, 1 = delete
  bytes  root_hash    = 3; // required if action = 0
  string manifest_uri = 4;
  uint32 anchor_type  = 5;
  int64  deposit      = 6; // additional lock, nano PAC; 0 on update/delete
  int64  fee          = 7;
  string memo         = 8;
  uint32 lock_time    = 9;
}
```

Wallet gRPC MUST be able to sign and broadcast the resulting raw tx like any other
payload. No new signature scheme.

`PayloadType.PAYLOAD_TYPE_ANCHOR = 7`

```protobuf
message PayloadAnchor {
  string from         = 1;
  uint32 action       = 2; // 0 = set, 1 = delete
  bytes  root_hash    = 3; // empty if action = 1
  string manifest_uri = 4;
  uint32 anchor_type  = 5;
  int64  deposit      = 6; // nano PAC; 0 on update/delete
}

// Inside TransactionInfo:
//   oneof payload { ... PayloadAnchor anchor = 36; }
```

#### 9.4 Change notifications

Nodes that enable ZeroMQ MUST publish a new topic:

```text
TopicAnchorInfo = 0x0005  // name: "anchor_info"
```

Body (after the 2-byte topic and sequence, same framing as other ZMQ topics):

| Field | Size | Notes |
| --- | --- | --- |
| Address | 21 | Account |
| Action | 1 | `0` Set, `1` Delete |
| Height | 4 | Including block, little-endian `uint32` |
| HashLen | 1 | `0` on delete |
| RootHash | HashLen | Omitted on delete |

Apps SHOULD treat ZMQ as a cache invalidation hint and re-read `GetAnchor` for the
canonical fields (timestamps, URI). Missed events MUST be recoverable via `ListAnchors`
or `GetAccount`.

The in-process `eventPipe` SHOULD emit the same information so the HTML/gRPC layers stay
consistent.

## Semantics

An anchor is **active** iff it is present on the account in the current state.

Delete removes current validity. Old txs, memos, and explorer history may still show that
an anchor once existed. Clients MUST use `GetAnchor` / `GetAccount.anchor`, not transaction
history, as the source of truth for "is this live?" and for timestamps.

`CreatedAt*` is the first attestation. `UpdatedAt*` is the last. After delete both are gone.

## Off-chain application profile (`PAC-ANCHOR-1`)

Nodes MUST NOT validate this section. It is the default convention so independent apps
(Stamp, DID, tickets, password vaults) produce compatible `RootHash` / `ManifestURI`
values. Apps MAY use another scheme; they SHOULD then pick a dedicated `AnchorType`
(`0xFF` or a future assigned value) so generic verifiers do not misread the digest.

### Hash of a single blob

```text
RootHash = BLAKE2b-256(content)   // 32 bytes, same as crypto/hash.Hash256
ManifestURI = optional locator of `content` (https, ipfs, …)
AnchorType = 0x00
```

Verification (client):

1. `GetAnchor(address)`. If `found == false`, the attestation is inactive.
2. Compare `root_hash` to `BLAKE2b-256(local_bytes)`.
3. Display `created_at_height` / `created_at_time` and `updated_at_*` from the slot.
   Do **not** recover the date from a pruned transaction.
4. If `manifest_uri` is set, fetching it is a client policy. Treat it as untrusted.
   After fetch, hash the bytes and require equality with `root_hash`.

### Many items under one slot

One native slot per account. Many files ⇒ one Merkle root off-chain.

1. Order items deterministically (UTF-8 path, bytewise).
2. Leaf `i` = `BLAKE2b-256(content_i)` (32 bytes).
3. Build a tree with Pactus `simplemerkle` (`HashMerkleBranches` of left||right,
   duplicate last leaf if odd).
4. `RootHash` = 32-byte Merkle root.
5. `ManifestURI` locates a UTF-8 JSON manifest of the form below.
6. Inclusion proof for one item is the standard Merkle path of that tree. Store and
   transmit the path **off-chain**. The chain only holds the root.

Example manifest:

```json
{
  "v": 1,
  "alg": "blake2b-256",
  "items": [
    { "name": "contract.pdf", "hash": "<64 hex chars>" }
  ]
}
```

`AnchorType` `0x00` remains correct for a raw Merkle root. Use `0x03` when the tree is
specifically a revocation registry, `0x01` for a service manifest document, `0x02` for a
DID document (single blob or its hash), `0xFF` for encrypted blobs.

### Proof page (informative)

A verifier page needs, and only needs:

* account address;
* `AnchorInfo` from a node the user trusts (or their own node);
* the content bytes (or Merkle leaf + path + manifest);
* optional: block header at `updated_at_height` if the user wants to cross-check time
  against a full node. A pruned node already printed `updated_at_time` from state.

No extra on-chain field is required for that loop.

## Activation

This change is not backward compatible: old nodes cannot decode payload type `7` and
cannot decode account records that carry a suffix.

Activation follows [PIP-51](./pip-51.md):

1. Implementations advertise protocol version **5**.
2. When more than **75%** of committee power supports version 5, proposers raise the
   block version to 5.
3. From that block onward, `TypeAnchor` is legal and account suffixes may appear.
4. Before that block, `TypeAnchor` MUST be rejected as an invalid payload type, and
   nodes MUST still persist accounts as 12-byte records.

No genesis replay. No bootstrap committee. No rollback.

Testnet SHOULD activate first, with the same encoding and `MinAnchorDeposit`.

## Test Cases

Consensus tests MUST include at least:

1. **Create** with `Deposit == MinAnchorDeposit`: account suffix present; `Balance`
   decreased by `Deposit+fee`; `LockedDeposit == Deposit`; state root changes.
2. **Create** with `Deposit == MinAnchorDeposit - 1`: rejected.
3. **Create** on unknown account: `AccountNotFound`.
4. **Update** with `Deposit == 0`: fields overwritten; `LockedDeposit` unchanged.
5. **Update** with additional `Deposit`: `LockedDeposit` increases without wrap.
6. **Delete** of existing slot: suffix gone (12-byte account); `Balance` increased by
   `locked - fee`; `GetAnchor` not found.
7. **Delete** with no slot: fail, state unchanged.
8. **Signer** validator or treasury address: `BasicCheck` fail.
9. **HashLen** 31 and 65: fail. **HashLen** 32 and 64: pass.
10. **URILen** 129: fail. Invalid UTF-8: fail. Empty URI: pass.
11. **Unknown Action** `2`: fail decode / `BasicCheck`.
12. **Overflow** `Deposit = MaxNanoPAC`, `fee > 0`: fail before add (PIP-54 class).
13. **Overflow** `LockedDeposit + Deposit` would wrap `int64`: fail.
14. **Transfer** after create cannot spend `LockedDeposit`.
15. **Delete** when `Balance == 0` but `LockedDeposit >= fee`: success (fee from refund).
16. **Pruned node**: after create, `GetAnchor` returns digest **and** `created_at_*` /
    `updated_at_*` without the creating tx body.
17. **Pre-v5 block**: payload type 7 rejected; 12-byte accounts still decode.
18. **Account decode**: 12-byte record → no anchor; well-formed suffix → anchor;
    truncated suffix → fail; `HasAnchor = 0` suffix → fail.
19. **Two Set txs** in one block for the same `From`: second sees the first's state
    (sandbox), both succeed if funds suffice; final slot is the second payload.
20. **Supply**: sum of `Balance + LockedDeposit` across accounts is conserved except for
    fees (fees follow the existing treasury accumulation path).
21. **Timestamps**: create sets all four fields from the including block. Update keeps
    `CreatedAt*` and refreshes `UpdatedAt*`. Payload cannot carry timestamps.
22. **Timestamp forgery**: a Set decoded with extra trailing timestamp bytes MUST fail.
23. **GetAccount** includes `anchor` when present; omits it when not.
24. **ListAnchors** pagination is deterministic by `Account.Number`.
25. **Delete** then `GetAnchor.found == false`.
26. **Sandbox** `CurrentUnixTime` equals the committed block `UnixTime`.

## Reference Implementation

None in `pactus-project/pactus` at the time of this revision. A follow-up PR against
the node is expected only after this PIP is **Accepted**.

## Rationale

**Why not a memo?**
Memos are history. Pruned nodes drop them. They cannot be revoked. They cannot be read
from the state root. They answer a different question.

**Why not a third Merkle tree / extra store prefix?**
A registry that is not in `stateRoot` is not consensus state. A third root would also
change `HashMerkleBranches(acc, val)`, which is a larger consensus change for no gain.
The account tree already has a stable per-account leaf index (`Account.Number`).

**Why one slot?**
Same bound PIP-48/PIP-49 used: one extra object per account. If an application needs many
digests, it Merkleizes off-chain and publishes one root. That is the intended use.

**Why 32–64 bytes, not `hash.Hash` (32)?**
Pactus itself uses BLAKE2b-256. Applications will also use SHA-256, SHA-512, SHA-3, or
a Merkle root from another tree. Capping at 64 keeps the suffix bounded.

**Why pay a deposit instead of a one-way fee?**
A one-way fee still leaves dead slots forever. A refundable lock prices occupation of
**current** state and makes exit rational. With ~thousands of accounts, worst-case extra
state is `< 2 kB × N_accounts`, but the lock still prevents "set and forget" litter.

**Why `MinAnchorDeposit = 1 PAC`?**
It reuses `MinimumStake`, is trivial to remember, and is far above the default fee.
It is a constant, not an economic-policy knob, so it does not belong in genesis JSON.

**Why fee-from-refund on delete?**
Otherwise an account that locked its entire `Balance` could never delete the slot.
That would trap both the deposit and the leaf.

**Why timestamps in state, not in the tx?**
Stamp-like apps need "this was attested at time T" after pruning. Tx bodies and even
old blocks may be gone. Height + Unix time copied from the including header is 16 bytes
and cannot be chosen by the signer.

**Why not put timestamps in the payload?**
Then a user could claim any date. They MUST come from the block the committee signed.

**Why `ListAnchors` and ZMQ if discovery is off-chain?**
Without them every app reimplements a full-node scanner. The walk is the same
`IterateAccounts` the node already has; ZMQ is the same event bus as `tx_info`. That is
Interface work, not a new consensus index.

**Why `PAC-ANCHOR-1` in a Core PIP?**
So two independent clients hash the same PDF the same way. It is explicitly non-consensus.
Leaving it out would force the first app to become an accidental standard.

## Alternatives Considered

1. **Memo convention** (`ANCHOR <hex>`). Rejected: pruning, no live revoke, no `GetAnchor`.
2. **Separate `AnchorRegistry` store prefix.** Rejected: not in `stateRoot` unless a third
   tree is added; more code, more failure modes.
3. **Embed the digest in `memo` and require full nodes.** Rejected: Pactus ships pruned
   mode on purpose. Consensus APIs must work for pruned nodes.
4. **PIP-48-style extra keys.** Out of scope; this PIP does not change signing.
5. **Variable number of slots.** Rejected: turns the account into a database. Merkleize.
6. **Store last TxID in the slot.** Rejected: after pruning the body is gone; height+time
   already answer the notary question.
7. **Account Merkle proofs vs `stateRoot`.** Useful for light clients, but `GetAccount`
   has no proof today. Out of scope; apps already trust their node for balances.

## Backwards Compatibility

* Old nodes cannot decode type `7` → they cannot follow version-5 blocks (PIP-51).
* Old 12-byte account records remain valid forever.
* Transfer / Bond / Unbond / Withdraw / Sortition / BatchTransfer encodings unchanged.
* `Account.Number` and spendable `Balance` semantics unchanged.
* No genesis change.

## Security Considerations

### Integer overflow (CWE-190, PIP-54)

Every sum involving `Deposit`, `Fee`, `Balance`, or `LockedDeposit` MUST reject before
add if `a > MaxNanoPAC - b`. `Value()` for Set is a single `Amount` (no loop), but
`Value() + Fee` and `LockedDeposit + Deposit` are still two-term sums and MUST be
checked. Tests 12–13 exist specifically so this class cannot ship again.

### Historical vs live confusion

Wallets and explorers MUST display "active" only from `GetAnchor`. Showing a past Anchor
transaction as a current attestation is a client bug, not a protocol guarantee.

### `ManifestURI` is untrusted

The protocol does not validate schemes. Clients MUST treat the string as attacker
controlled (phishing, `javascript:`, huge unicode, IPFS bait). Do not auto-open.

### Impersonation

An anchor proves that **this key** currently attests to a digest. It does not prove
identity, legal identity, or that the URI content is honest. Binding a human name to an
address is an application problem.

### External availability

`RootHash` does not store the file. If the URI goes offline, the digest remains, the
bytes do not.

### State bloat

Upper bound: one suffix per account, ≤ 220 extra bytes. Occupation costs
`MinAnchorDeposit` until delete. There is no per-block growth from unused slots.

### Block-time honesty

`CreatedAtTime` / `UpdatedAtTime` are the proposer's block Unix time, the same trust
model as any other Pactus timestamp. A proposer can skew `UnixTime` within whatever
bounds the current protocol already accepts. Height is the authoritative order.

### Executor-only timestamps

Any implementation that accepts timestamp fields from the payload is non-compliant.
Tests 21–22 exist so this cannot ship.

### Fee market / griefing

Anyone can create their own slot. Nobody can overwrite or delete another account's slot:
`Signer()` is `From`, and `From` must match the account whose state is mutated.

### Replay

Normal `LockTime` / TTL rules apply. No extra nonce. A replayed Delete after a later
re-create would delete the **new** slot if it is still in TTL and the account still
signs… Replay requires the original signature, which is bound to the original payload
(including `Action` and, for Set, the digest). A Set replay may update the slot back to
an old digest if the signed payload is still inside TTL; that is the same class of issue
as replaying a Transfer and is mitigated by `TransactionToLiveInterval` (one day).

## Use Cases (informative)

These are application patterns. None of them are protocol rules.

* DID / profile document: URI + hash, delete to revoke the profile.
* Revocation registry: publish a Merkle root; update the root; delete to retire the issuer.
* Document integrity: stamp a PDF hash (the Stamp client).
* Ticket / event lists: Merkleize off-chain, one root on-chain.
* Service manifest: operator publishes an endpoint descriptor hash.

## Acknowledgments

The account-suffix design follows PIP-49's "one optional slot on an existing object"
pattern. Amount checks follow PIP-54. Activation follows PIP-51.
