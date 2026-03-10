---
pip: 50
title: Native State Anchoring (Pruning-Resistant Live State Slot)
author: Johan (@johan256x)
status: Draft
type: Standards Track
category: Core
discussion-no:
created: 2026-03-08
---

## Abstract

This proposal introduces a lightweight "State Anchor" mechanism directly in the Pactus Global State. It allows an account to reserve a single persistent state slot containing a cryptographic commitment, an optional manifest URI, and a one-byte application type tag.

Unlike transaction payloads such as memos or metadata, which belong to blockchain history and may become harder to access under pruning or archival policies, a State Anchor resides in the current global state. This makes the anchor directly readable from the current chain state without requiring historical transaction bodies.

This proposal is not intended to store application data on-chain. Its purpose is to maintain a minimal, live on-chain proof of integrity and authenticity for externally stored data.

To prevent state bloat, the mechanism is opt-in and protected by a locked deposit. The deposit is recoverable when the anchor is removed, at which point the state entry is deleted.

## Motivation

### 1. History vs. Current State

Transaction memos and similar payloads are immutable, but they belong to blockchain history. As the chain grows, nodes may prune historical data to reduce storage costs.

This creates an availability asymmetry: a proof may have existed historically, but applications may have to rely on archival infrastructure to retrieve and validate it. For certain categories of data, that is not desirable. Some applications need a minimal proof to remain directly readable from the current network state.

This proposal addresses that need by defining a small, bounded, live state object that can remain available at the head of the chain.

### 2. Live Validity Rather Than Historical Existence

A State Anchor is not merely an old trace proving that some data once existed. It is a live protocol-level registration that is valid only while it exists in the current state.

The anchor is valid only while it exists in the current state.
Withdrawal removes both the locked deposit and the live anchor entry.
Historical traces may remain in blockchain history, but the anchor must no longer be treated as active or usable.

This distinction is important. An external indexer that only scans historical transactions may still observe a prior publication even after removal. That is not sufficient for applications that need current validity semantics.

### 3. Minimal Native Primitive for External Data Integrity

This proposal does not aim to replicate decentralized storage, rich registries, or smart-contract-level application logic. Instead, it provides a minimal native primitive for external data:

* a cryptographic commitment proving integrity
* an optional URI pointing to external content or metadata
* a small type tag for application-level classification
* a deposit-backed lifecycle with explicit deletion

This gives applications a stable and canonical protocol-level anchor without requiring a separate contract or convention.

## Goals

* Provide a minimal live state anchor for externally stored data
* Keep the state footprint small and bounded
* Make anchor validity depend on current state presence
* Allow explicit removal and deposit recovery
* Support simple application-level classification via AnchorType
* Keep discovery outside consensus while remaining easy to index off-chain

## Non-Goals

* Storing full application data on-chain
* Defining a full decentralized discovery or directory protocol
* Enforcing URI formats, content schemas, or application semantics
* Maintaining on-chain secondary indexes by AnchorType
* Replacing smart contracts or richer application layers

## Specification

### 1. State Storage: Anchor Registry

The protocol introduces a sparse key-value map in the global state called AnchorRegistry.

Key:
AccountAddress (20 bytes)

Value:
AnchorData (bounded size)

Each account may own at most one anchor entry.

Suggested structure:

type AnchorData struct {
RootHash      []byte
ManifestURI   string
AnchorType    uint8
LockedDeposit int64
}

Field semantics:

RootHash
A cryptographic commitment to externally stored content or to an application-defined structure such as a Merkle root.
Length MUST be between 32 and 64 bytes inclusive.

ManifestURI
An optional UTF-8 encoded URI or identifier pointing to externally stored metadata or content.
Encoded byte length MUST be less than or equal to 128 bytes.
The protocol stores this field as opaque UTF-8 text and does not validate URI scheme or content.

AnchorType
A one-byte application classification hint.
The protocol stores this field but does not validate application semantics.

LockedDeposit
The amount of NanoPAC currently locked for maintaining the state slot.

### 2. AnchorType Registry

AnchorType is a lightweight client hint intended for application-level classification. It does not create protocol-level behavior and must not be interpreted as an on-chain authorization or execution flag.

Standardized values:

* 0x00 = Raw Data / Generic Commitment
* 0x01 = Service Manifest
* 0x02 = DID Document
* 0x03 = Verifiable Credential / Revocation Registry
* 0x04 to 0xFE = Reserved
* 0xFF = Private / Encrypted / Proprietary Usage

The Reserved range is intentionally left undefined for future standardization without changing the field format.

### 3. Transaction Payload

A new transaction payload type, PayloadTypeAnchor, is introduced.

It supports three operations:

* create
* update
* delete

The exact binary encoding is implementation-defined here, but the payload must carry enough information to distinguish between:

* setting or updating anchor fields
* explicitly removing the anchor

### 4. Validation Rules

#### For create or update operations:

1. RootHash length MUST be between 32 and 64 bytes inclusive.
2. ManifestURI, if present, MUST be valid UTF-8.
3. ManifestURI encoded byte length MUST be less than or equal to 128 bytes.
4. AnchorType is a single byte and may take any value, but only the standardized values listed in this proposal have defined meanings.
5. The resulting locked deposit for the account MUST be greater than or equal to MinAnchorDeposit.

#### For delete operations:

1. The request MUST explicitly indicate deletion.

2. If no anchor exists for the sender account, the transaction MUST fail or no-op according to the chain’s standard missing-state mutation policy.

3. On success, the locked deposit is refunded and the anchor entry is deleted from state.

4. Deposit Rules

MinAnchorDeposit is a protocol parameter defined by the chain implementation and may change across protocol versions.

#### Rules:

* Creating an anchor requires the resulting locked deposit to be at least MinAnchorDeposit.
* Updating an existing anchor does not require additional deposit if the currently locked amount already satisfies the minimum required at the time the anchor was created or last validly updated under prior rules.
* If MinAnchorDeposit decreases in a later protocol version, the account may be allowed to recover the excess locked amount, provided the remaining deposit still satisfies the active minimum and the chain implementation supports this operation.
* If MinAnchorDeposit increases later, existing anchors are not required to top up automatically solely because of the parameter change.

### 5. Execution Logic

#### Create / Update

If the payload contains anchor data:

1. Determine whether an anchor already exists for the sender account.
2. Transfer Tx.Value, if any, from the sender balance into LockedDeposit.
3. Overwrite RootHash, ManifestURI, and AnchorType with the new values.
4. Persist the resulting AnchorData into AnchorRegistry under the sender address.

#### Delete / Withdrawal

If the payload explicitly requests removal:

1. Refund the full LockedDeposit to the sender balance.
2. Delete the corresponding entry from AnchorRegistry.
3. Release the occupied state entry so the live network cost returns to zero for that account.

## Semantics

An anchor is considered active only if it is present in the current state.

When the deposit is withdrawn, the corresponding anchor entry is removed from state.

Historical records of prior existence may remain in blockchain history, but they have no effect on the anchor’s current validity or usability.

## Reading and Discovery Model

Canonical read path

The canonical lookup method is by account address:
GetAnchor(AccountAddress)

This proposal defines the protocol-level state object. It does not require the consensus layer to maintain secondary indexes by AnchorType or any other derived field.

## Discovery

Global discovery is outside consensus scope.

Applications, wallets, explorers, and indexers may build their own derived views over anchors. This includes filtering by AnchorType, fetching and validating ManifestURI contents, and presenting richer service or identity directories.

### Node assistance

Node implementations may expose helper interfaces to make external indexing cheaper, for example:

* paginated iteration over AnchorRegistry
* registry snapshot export
* filtered export in implementation-specific APIs
* event streams for create, update, and delete operations

Such interfaces are optional implementation conveniences. They are not part of consensus and do not alter canonical state semantics.

## Use Cases

### 1. Identity and DID Publication

An account may publish an anchor whose ManifestURI points to a DID document or related metadata. The RootHash commits to the expected external content. Applications can verify that the retrieved document matches the commitment and that the anchor is currently active.

### 2. Verifiable Credential Revocation Registries

An issuer may publish a Merkle root or equivalent commitment representing a revocation registry. Verifiers can use the live anchor as the authoritative current commitment while the anchor remains active in state.

### 3. Service Manifests

An operator may publish a manifest describing a service endpoint, protocol support, or service metadata. The anchor provides a stable protocol-level proof that the manifest content matches the commitment published by that account.

### 4. Event and Ticketing Registries

An organizer may publish a commitment to an event registry, ticket manifest, or Merkle root of valid tickets. The anchor does not store ticket data itself. It only provides a live proof of integrity and provenance for externally stored event data. If the anchor is removed, that publication must no longer be treated as active.

### 5. Document and Evidence Integrity Proofs

An account may anchor the hash or Merkle root of externally stored documents such as legal records, compliance evidence, or signed artifacts. The anchor allows applications to verify that retrieved content has not been modified since publication.

### 6. Application-Level Merkleized Registries

Applications may maintain large mutable registries off-chain while publishing only the current root commitment on-chain. This allows efficient external data management while preserving protocol-level integrity and current-state validity.

## Rationale

Why not store full application data on-chain?

The purpose of this proposal is not data storage. It is to maintain a minimal, live state commitment to externally stored data. That gives applications an integrity and authenticity anchor without imposing large and unbounded state growth on the chain.

Why 1 account = 1 slot?

The one-account-one-slot rule keeps the primitive simple, bounded, and predictable. It prevents a single account from using this mechanism as a general-purpose on-chain database, limits worst-case per-account state growth, and makes the feature easier to reason about for wallets, explorers, and implementations. Applications that need more complex registries can still place richer structures off-chain and commit only a root or manifest through the single live anchor.

Why 32 to 64 bytes for RootHash?

A 32-byte hash is sufficient for common modern commitments such as SHA-256 or BLAKE3 outputs. Allowing up to 64 bytes preserves compatibility with stronger or future-proof formats without forcing the overhead on everyone. The field is intentionally flexible while still remaining tightly bounded.

Why AnchorType instead of richer on-chain metadata?

A one-byte type tag is a compact and low-cost classification hint. Richer human-readable metadata would increase state size, raise phishing and naming issues, and push application-specific concerns into the protocol. The type tag plus an external manifest is a more efficient separation of concerns.

Why no on-chain secondary index by AnchorType?

Maintaining derived indexes in consensus would increase state size, update complexity, and implementation surface. This proposal intentionally stores only the canonical minimal state object. Discovery and derived views are better handled by external applications and node-level helper interfaces.

Why UTF-8 for ManifestURI?

UTF-8 is the standard interoperable text encoding used across modern software stacks. Requiring valid UTF-8 ensures consistent storage and decoding behavior across implementations while still treating the field as opaque application-level content.

## Resistance to State Bloat

The locked deposit acts as an economic filter. The feature is opt-in, the slot count is strictly bounded to one per account, the payload is small, and removing the anchor recovers the deposit while deleting the live state entry. Together, these properties constrain long-term growth and encourage retention only for anchors that remain useful.

## Backwards Compatibility

This proposal requires a hard fork to introduce:

* AnchorRegistry in the global state
* PayloadTypeAnchor transaction support
* associated validation and execution logic

It does not require changes to the standard account structure beyond the introduction of the separate registry and does not alter ordinary transfer semantics.

## Security Considerations

### 1. Historical confusion

Applications must distinguish between historical existence and current validity. The authoritative signal is current state presence, not the mere fact that an anchor once appeared in transaction history.

### 2. Malicious ManifestURI values

The protocol does not validate URI schemes, content type, or safety. Client software must sanitize and handle ManifestURI values safely before displaying or dereferencing them.

### 3. Phishing and impersonation

Anchor presence does not prove that an account is trustworthy in a social or legal sense. Users and applications must still verify that the publishing account is the expected one.

### 4. External data availability

The anchor proves integrity and provenance of external data, but it does not guarantee that external content remains reachable. Availability of off-chain content remains an application or infrastructure concern.

### 5. Reserved type values

Values in the Reserved range have no standardized meaning in this proposal and must not be interpreted by clients as if they were already assigned.
