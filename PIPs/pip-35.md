---
pip: 35
title: Using Nanomsg and NNG (Nanomsg next generation)
author: Muhammad Javad Akbarian (@akbariandev)
status: Draft
type: Informational
category: Informational
created: 2024-11-14
---

## Abstract

This proposal shows the information about Nanomsg and next generation of Nanomsg protocol that is used in Pactus.

## Motivation

Using a stable bidirectional communication protocol is an important object in a P2P network.
Nanomsg provides this ability over socket protocol.
This library supports multiple patterns like Survey, PUB/SUB, Pipeline, etc.
Now by improving and enhancing some features of nanomsg, the NNG (nanomsg next generation) born.
The most important thing for this new generation is supporting multiple threads to handle lots of socket connections and
also supporting more operating systems.

## Specifications

To ensure that Nanomsg is the best library to use, here we provide compare list between Nanomsg, gRPC and Cap’n Proto.

### Why using Nanomsg (in case of PUB/SUB)

| Feature                    | **Nanomsg**                       | **gRPC**                          | **Cap’n Proto**                   |
|----------------------------|-----------------------------------|-----------------------------------|-----------------------------------|
| **Native Pub/Sub Support** | Yes                               | Limited (not built-in)            | No                                |
| **Implementation Style**   | Built to support various messaging patterns, including pub/sub. Utilizes sockets for easy implementation of pub/sub architectures. | Primarily designed for RPC communication, but can simulate pub/sub using streaming RPCs and service definitions. | Focused on serialization; does not offer pub/sub features directly. |
| **Performance**            | High-performance messaging with low overhead, suitable for pub/sub applications. | High performance with gRPC, but overhead might increase due to the RPC model. Streaming can add complexity. | High-speed serialization, but not applicable directly to pub/sub. |
| **Ease of Use**            | Provides a simple API for pub/sub; easy to implement in networks. | Requires more setup for pub/sub; mainly designed for RPC-style communication. | Not applicable; focused on serialization rather than messaging protocols. |
| **Message Delivery**       | Supports reliable messaging patterns, including delivery guarantees depending on the socket type used (e.g., PUB/SUB pattern). | Lacks inherent message delivery guarantees in pub/sub context; focuses on request/response patterns. | Not applicable; does not handle message delivery or communication. |
| **Protocol Type**          | Socket-based messaging library, allowing direct P2P connections with pub/sub patterns. | RPC framework using HTTP/2 with binary serialization (Protocol Buffers). Not optimized for pub/sub out of the box. | Serialization framework focused on efficiency but does not encapsulate transport or messaging semantics. |

With above information we ensure that Nanomsg is the best choice to implement PUB/SUB pattern in Pactus project.
After that some other supported scalability protocols listed below.
With these kinds of protocols we ensure to have lots of use-cases in Pactus network.

* **PAIR:** simple one-to-one communication
* **BUS:** simple many-to-many communication
* **REQREP:** allows to build clusters of stateless services to process user requests
* **PIPELINE:** aggregates messages from multiple sources and load balances them among many destinations
* **SURVEY:** allows to query state of multiple applications in a single go

### NNG and Nanomsg enhancements

NNG is an improvement lib on Nanomsg. In below table there is some description about NNG and the difference to Nanomsg.
The NNG has compatibility to Nanomsg and can be implemented by [mangos](https://github.com/nanomsg/mangos).

|               |                                                                                                                                                                                                                                                                        |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Scalability   | NNG scales out to engage multiple cores using a bespoke asynchronous I/O framework, using thread pools to spread load without exceeding typical system limits.                                                                                                         |
| Extensibility | Because it avoids ties to file descriptors, and avoids confusing interlocking state machines, it is easier to add new protocols and transports to NNG.  This was demonstrated by the addition of the TLS and ZeroTier transports.                                      |
| Security      | NNG provides TLS 1.2 and ZeroTier transports, offering support for robust and industry standard authentication and encryption. In addition, it is hardened to be resilient against malicious attackers, with special consideration given to use in a hostile Internet. |
