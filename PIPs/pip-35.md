---
pip: 35
title: Comparison of communication protocols
author: Muhammad Javad Akbarian (@akbariandev)
status: Draft
type: Informational
category: Informational
discussion-no: 201
created: 2024-11-14
---

## Abstract

This proposal shows the compare list between some communication protocols and frameworks to use in Pactus blockchain.

## Motivation

Using a stable bidirectional communication protocol is an important part of Pactus blockchain.
The purpose of using this protocol is to cover the event streaming and PUB/SUB messaging between nodes and clients.
To have this ability we need to know the difference between each protocol and frameworks and select the best one.

## Specifications

Here we compared 9 protocols in terms of simplicity, resource consumption, community size and implementation libraries.

### Compare list

| Protocol                   | Simplicity        | Community | Implementation                                                   | Resource Consumption          |
|----------------------------|------------------|-------------------------|------------------------------------------------------------------|-------------------------------|
| **MQTT**                   | Simple           | Large                   | [Eclipse Paho MQTT](https://github.com/eclipse/paho.mqtt.golang) | Low (designed for lightweight devices) |
| **AMQP**                   | Moderate         | Moderate                | [RabbitMQ Go Client](https://github.com/streadway/amqp)          | Moderate (runs a broker, can be optimized) |
| **XMPP**                   | Moderate         | Large                   | [Go XMPP](https://mellium.im)                                    | Moderate (similar to AMQP)   |
| **NATS**                   | Simple           | Growing                 | [NATS Go Client](https://github.com/nats-io/nats.go)             | Low (lightweight and efficient) |
| **Apache Kafka**           | Complex          | Large                   | [sarama](https://github.com/Shopify/sarama)                      | High (more robust features, higher overhead) |
| **Apache Pulsar**          | Moderate         | Growing                 | -                                                                | Moderate to High (depending on usage) |
| **ZeroMQ**                 | Moderate         | Moderate                | [Go ZeroMQ](https://github.com/pebbe/zmq4)                       | Low to Moderate (depends on pattern) |
| **CoAP**                   | Simple           | Small                   | [Go CoAP](https://github.com/go-ocf/go-coap)                     | Low (optimized for constrained devices) |
| **Nanomsg**                | Simple           | Moderate       | [mangos](https://github.com/nanomsg/mangos)                      | Low to Moderate (simple API, lightweight) |

### Conclusion

With above information we can make decision that which protocol is the best.
In terms of simplicity Nonomsg, MQTT, NATS and CoAP are completely simple. But in terms of community, CoAP don't have
a large community.

After that to ensure about good implementation, we need to have a stable and reliable libraries.
The NATS supports lots of languages ([see this link](https://nats.io/download/)) and also MQTT have a complete list of
languages to support ([see here](https://mqtt.org/software/)). But Nanomsg and CoAp may have hard path for
implementations since they have less supported languages.

At the end to be aware of huge resource consumption, this proposal suggest to use MQTT, NATS and Nanomsg since they
designed to work on different hardware and operating systems and some of them like MQTT works well in IOT platforms.
