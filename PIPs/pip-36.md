---
pip: 36
title: ZeroMQ Notification Service
description: Real-time notification service for Pactus using ZeroMQ PUB/SUB
author: Pactus Development Team <info@pactus.org>
status: Final
type: Standards Track
category: Core
discussion-no: 206
created: 2024-12-16
---

## Abstract

This proposal introduces a notification service for Pactus blockchain based on the ZeroMQ PUB/SUB protocol.

## Motivation

Currently, the Pactus blockchain does not provide a standardized notification service to
alert applications about new blocks or transactions.
Such a service would be especially beneficial for applications like wallets,
which need real-time updates on transaction status changes, such as when a transaction becomes confirmed.

This proposal aims to define basic notifications for Pactus,
laying the groundwork for expanding notification capabilities in the future.

In [PIP-35](./pip-35.md), we evaluated and compared several communication protocols,
concluding that ZeroMQ is a suitable choice for this purpose.
ZeroMQ has been successfully implemented in other blockchains such as
[Bitcoin](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md),
[Monero](https://github.com/monero-project/monero/blob/master/docs/ZMQ.md), and
[Zcash](https://github.com/zcash/zcash/blob/master/doc/zmq.md), etc, making it a proven and reliable solution.

## Specifications

### What is ZeroMQ?

ZeroMQ is a high-performance asynchronous messaging library that provides a message queue but
operates without requiring a dedicated message broker.
It supports various messaging patterns, including publish/subscribe, request/reply, and push/pull,
making it highly versatile for decentralized systems like blockchain.

In the PUB/SUB pattern, ZeroMQ allows publishers to broadcast messages to multiple subscribers efficiently.
Subscribers receive only the messages relevant to their subscribed topics.
This pattern fits well for blockchain notifications,
where multiple clients may need updates about specific events like new blocks or transaction statuses.

### Message Format

Messages in ZeroMQ, following the Pactus message format,
begin with a 2-byte Topic ID, followed by topic-specific data and a 4-byte sequence number,
The sequence number, which acts as an incremental counter for each Topic ID and
is encoded in little-endian format, helps detect lost messages by tracking the message count.

![Pactus zeroMQ Message Format](../assets/pip-36/pactus_zeromq.png)

#### Topic ID

Topic ID is a fixed lenght two bytes and defined as below:

1. **0x0001**: Block Info
2. **0x0002**: Transaction Info
3. **0x0003**: Raw Block
4. **0x0004**: Raw Transaction

### Topic Data

The topic data contains variable-length information specific to each topic, as outlined below:

#### Block Info

The Block Info topic data is structured as:

```text
<Proposer Address: 21 bytes> + <Block Time in Unix: 4 bytes> + <Total Txs: 2 bytes> + <Block Number: 4 bytes>
```

#### Transaction Info

The Transaction Info topic data is structured as:

```text
<Transaction ID: 32 bytes> + <Block Number: 4 Bytes>
```

The block number indicates the block in which the transaction is confirmed.
If the block number is set to `0`, the transaction remains unconfirmed.
This allows the service to notify applications when transactions enter the transaction pool, with room for future expansion.

#### Raw Block Header

The Raw Block Header topic data is structured as:

```text
<Raw Block Header: 138 bytes> + <Block Number: 4 Bytes>
```

#### Raw Transaction

The Raw Transaction topic data is structured as:

```text
<Raw Transaction: Variable Length> + <Block Number: 4 Bytes>
```

### Configuration

In the configuration file, the following items should be added under the `[zeromq]` section:

```toml
# `zeromq` contains configuration options for the ZeroMQ notification service.
[zeromq]

  # `zmqpubblockinfo` specifies the address for publishing block info notifications.
  # Example: 'tcp://127.0.0.1:28332'
  # Default is '', meaning the topic is disabled
  zmqpubblockinfo = ''

  # `zmqpubtxinfo` specifies the address for publishing transaction info notifications.
  # Example: 'tcp://127.0.0.1:28332'
  # Default is '', meaning the topic is disabled
  zmqpubtxinfo = ''

  # `zmqpubrawblock` specifies the address for publishing raw block notifications.
  # Example: 'tcp://127.0.0.1:28332'
  # Default is '', meaning the topic is disabled
  zmqpubrawblock = ''

  # `zmqpubrawtx` specifies the address for publishing raw transaction notifications.
  # Example: 'tcp://127.0.0.1:28332'
  # Default is '', meaning the topic is disabled
  zmqpubrawtx = ''

  # `zmqpubhwm` defines the High Watermark (HWM) for ZeroMQ message pipes.
  # This parameter determines the maximum number of messages ZeroMQ can buffer before blocking the publishing of further messages.
  # The watermark is applied uniformly to all active topics.
  # Default is 1000
  zmqpubhwm = 1000
```

The socket type is PUB and the address must be a valid ZeroMQ socket address.
The same address can be used in more than one notification.

The High Watermark (HWM) defines the capacity of ZeroMQ's internal message pipes.
For simplicity, the watermark number is applied to all active topics.

Leaving an address empty in the configuration file will disable the corresponding topic.
