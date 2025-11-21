---
pip: 47
title: Decentralized Wallet-to-Wallet Messaging
description: Standard for enabling private, end-to-end encrypted messaging between Pactus wallet addresses.
author: Page900 (@Page900)
status: Draft
type: Standard
category: Interface
created: 2025-11-21
---

## Abstract

This PIP proposes the adoption of a Decentralized Wallet-to-Wallet Messaging (DWM) standard for
the Pactus ecosystem. The goal is to allow any Pactus wallet user to send a private,
end-to-end encrypted message directly to another Pactus address owner, functioning similarly to
a decentralized instant messaging application. This feature may operate off-chain to maintain
Pactus network efficiency, using cryptographic signing for identity verification, and prioritizing
robust security against phishing and malware.

## Motivation

Pactus users currently lack a secure, native communication method tied to their on-chain identity,
forcing them to use fragmented and centralized Web2 apps. This DWM standard addresses this gap
by:

**Security First:** Creating a communication channel that is inherently safer than traditional
platforms for Web3 users, specifically by neutralizing common phishing and malware vectors.

**Enabling True Web3 Communication:** Establishing a dedicated layer where identity is derived
from the Pactus wallet, fostering a cohesive and direct Web3 community.

**Enhancing User Experience:** Providing a seamless way to send thank-you notes, payment
confirmations, or negotiate terms without revealing personal contact information.

## Specification

This proposal advocates for adopting an existing, established open-source protocol (such as XMTP
"Extensible Message Transport Protocol" or a similar standard) or creating a reliable protocol
and integrating it with the Pactus wallet structure.

### 1. Message Identity and Encryption

**Identity Verification:** The sender must cryptographically sign the message using the private key
associated with their Pactus address.

**End-to-End Encryption (E2EE):** Messages must be secured with E2EE. Only the sender and the
designated recipient can decrypt and read the message.

### 2. Off-Chain Message Relay

**Blockchain Storage:** Message data may or may not be stored on the Pactus blockchain as a
transaction.

**Decentralized Network:** Messages may or may not be routed and temporarily stored by a
decentralized messaging network.

### 3. Wallet Implementation (Interface & Notifications)

Pactus client applications, primarily the existing Web Wallet, and future clients (GUI, CLI, and
mobile wallets) can be updated to support the DWM standard.

**Discovery:** Allow users to initiate a chat simply by entering a recipient's Pactus address.

**Signing/Sending:** Integrate the cryptographic functions (as per Section 1) to sign and send
the message via the off-chain network.

**Interface:** Offer a dedicated, user-friendly inbox and chat interface to view, send, and manage
messages.

**Notifications:** Integrate platform-native notification capabilities (e.g., browser notifications
for the Web Wallet) to alert the user of a new incoming message, even when the application is not
active.

- Notifications must be disabled by default (Opt-In Security).
- Notification content must be sanitized or encrypted; the full, cleartext message must require
  opening the app and decryption.

### 4. Link and File Security (Critical)

The wallet interface must implement multiple layers of defense against dangerous links and files:

**Link Sanitization and Warnings (Phishing Prevention):**

- All URLs must be displayed as plain text and NOT be clickable by default.
- A prominent, dismissible security warning must appear when a message contains a link from an
  unverified or non-transacted address.
- Shortened URLs (like Bit.ly) must be expanded and displayed in full before the user is given
  an option to click.

**File and Attachment Restrictions (Malware Prevention):**

- The DWM specification prohibits the sending or sharing of executable files (e.g., .exe, .zip,
  .js, .bat, .apk) entirely.
- Any supported files (images, simple documents) must be managed to prevent direct download to
  the user's primary file system.

### Implementation Stages

**Stage 1: Protocol Selection (Informational PIP):** A separate PIP should first be created to
evaluate and recommend the specific off-chain messaging protocol (e.g., XMTP, Push Protocol, etc.)
best suited for integration with Pactus's architecture.

**Stage 2: Wallet Integration (Interface PIP):** Once the protocol is chosen, development and
integration work must occur within the Pactus wallet applications to support the messaging
interface, cryptographic functions, link security, and the notification system.

## Backwards Compatibility

This PIP introduces new functionality and does not modify existing Pactus protocol behavior.
Wallets that do not implement DWM will continue to function normally. Messages sent via DWM will
not affect wallets that do not support this feature, ensuring full backwards compatibility.

## Test Cases

Test cases will be defined in subsequent implementation PIPs once the specific messaging
protocol is selected. At minimum, test cases should cover:

- Successful message encryption and decryption between two compatible wallets
- Verification of cryptographic signatures
- Proper handling of messages from non-transacted addresses
- Link sanitization and security warning display
- File type restrictions enforcement
- Notification opt-in/opt-out functionality
- Rate limiting and spam prevention mechanisms

## Reference Implementation

A reference implementation will be provided in Stage 2 (Wallet Integration PIP) once the
messaging protocol is selected and integration work begins.

## Security Considerations

### Spam Prevention & Consent (Opt-In)

The wallet must default to the most secure setting. Users must have a clear option to set a
contact filter (e.g., "Allow only messages from addresses I have transacted with").

Messages from addresses that are not consented to should be placed in a separate "Message
Requests" or "Spam" folder and must not trigger notifications.

Mechanisms like rate limits may be considered to prevent mass-spamming.

### Private Key Security

The wallet must ensure the private key is only used for signing (proving identity) and is never
exposed to the messaging relay network.

### Data and Notification Privacy

Notifications and all message data must adhere to E2EE principles and not leak cleartext content
outside of the secured Pactus application environment.

### Phishing and Malware Mitigation

The link sanitization and file restriction requirements specified in Section 4 are critical
security measures designed to prevent common attack vectors:

- **Phishing Prevention:** By displaying URLs as plain text and requiring explicit user action,
  users can verify links before clicking, reducing the risk of phishing attacks.
- **Malware Prevention:** By prohibiting executable files and managing file downloads, the risk
  of malware distribution through the messaging system is minimized.

### Network Security

The off-chain messaging network must implement appropriate security measures to prevent
message interception, tampering, or replay attacks. The specific security requirements will be
detailed in the protocol selection PIP (Stage 1).
