---
pip: 23
title: Sign and verify message by public and private key account
author: Javad Rajabzadeh (@ja7ad)
status: Accepted
type: Standards Track
discussion-no: 102
category: Interface
created: 14-04-2024
---

## Abstract

The purpose of this proposal is to introduce a standardized method for signing and verifying messages using public and
private key pairs associated with Pactus accounts.

## Motivation

Digital signatures play a crucial role in ensuring the authenticity and
integrity of messages exchanged within the Pactus network.
Currently, Pactus provides the capability to sign transactions,
but lacks a standardized approach for signing arbitrary messages.
By implementing a consistent method for signing and verifying messages using public and private key pairs,
we can enhance the security and interoperability of Pactus-based applications.
This proposal aims to address this gap by introducing a simple yet powerful mechanism for signing and
verifying messages, thereby enabling a wide range of use cases such as secure communication, authentication,
and data integrity verification on the Pactus blockchain.

## Specification

The proposed method for signing and verifying messages shall follow the following steps:

1. **SignMessageWithPrivateKey** (Util Service)
   - Input: Message as string, Private key associated with Pactus account as string.
   - Output: Signature as hex
   - Procedure: Use the private key to generate a cryptographic signature for the input message.

2. **VerifyMessage** (Util Service)
   - Input: Message as string, Signature as hex, Public key as string
   - Output: Boolean indicating the validity of the signature
   - Procedure: Use the public key to verify the authenticity of the signature for the input message.

3. **SignMessage** (Wallet Service)
   - Input: Wallet Name as string, Password for wallet (optional), Message as string, Account address as string
   - Output: Signature as hex
   - Procedure: Use the private key specific account address in wallet to generate a cryptographic
   signature for the input message.

## Backward Compatibility

This proposal introduces a new feature to the Pactus blockchain and does not impact existing functionalities or
data structures within the network. Existing applications and systems operating on the Pactus blockchain
can seamlessly adopt the proposed message signing and verification mechanism without requiring any modifications.

## Security

The security of this proposal hinges on the strength and reliability of the cryptographic algorithms employed for
signing and verifying messages. It is imperative to utilize well-established cryptographic standards and
libraries to mitigate the risk of signature forgery and unauthorized access.
Furthermore, stringent measures should be implemented to safeguard private keys and prevent unauthorized disclosure,
as the compromise of a private key could lead to unauthorized message signing and
potential security vulnerabilities within the Pactus blockchain network.
