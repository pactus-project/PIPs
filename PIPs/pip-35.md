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

| Protocol                   | Simplicity        | Community | Implementation                                                   | Resource Consumption          | Using Broker |
|----------------------------|------------------|-------------------------|------------------------------------------------------------------|-------------------------------|--------------|
| **MQTT**                   | Simple           | Large                   | [Eclipse Paho MQTT](https://github.com/eclipse/paho.mqtt.golang) | Low (designed for lightweight devices) | YES          |
| **AMQP**                   | Moderate         | Moderate                | [RabbitMQ Go Client](https://github.com/streadway/amqp)          | Moderate (runs a broker, can be optimized) | YES          |
| **XMPP**                   | Moderate         | Large                   | [Go XMPP](https://mellium.im)                                    | Moderate (similar to AMQP)   | YES          |
| **NATS**                   | Simple           | Growing                 | [NATS Go Client](https://github.com/nats-io/nats.go)             | Low (lightweight and efficient) | YES          |
| **Apache Kafka**           | Complex          | Large                   | [sarama](https://github.com/Shopify/sarama)                      | High (more robust features, higher overhead) | YES          |
| **Apache Pulsar**          | Moderate         | Growing                 | -                                                                | Moderate to High (depending on usage) | YES          |
| **ZeroMQ**                 | Moderate         | Moderate                | [Go ZeroMQ](https://github.com/pebbe/zmq4)                       | Low to Moderate (depends on pattern) | NO           |
| **CoAP**                   | Simple           | Small                   | [Go CoAP](https://github.com/go-ocf/go-coap)                     | Low (optimized for constrained devices) | NO           |
| **Nanomsg**                | Simple           | Moderate       | [mangos](https://github.com/nanomsg/mangos)                      | Low to Moderate (simple API, lightweight) | NO           |

### Simplicity & Implementation

In terms of simplicity Nonomsg, MQTT, NATS and CoAP are completely simple. They have few keywords, methods and
simple structure to use.
After that to ensure about good implementation, we need to have a stable and reliable libraries.
The NATS supports lots of languages ([see this link](https://nats.io/download/)) and also MQTT have a complete list of
languages to support ([see here](https://mqtt.org/software/)). in other side, Nanomsg and ZeroMQ have good resources
but not much enough as NATS and MQTT.
And finally we may have difficult path to implement CoAP since it has less supported languages.

### Broker

The broker is a centralized handler with a specific queue that will add more reliability and scalability to protocols.
But in our case the broker may need extra works for implementation and deployment.
The broker is an independent part of each protocol and this is a negative point for us.
As you can see in above list only ZeroMQ, CoAP and Nanomsg are free of broker and this may be an important parameter
to select them for Pactus project.

### Resource Consumption

At the end to be aware of huge resource consumption, we can think about NATS, MQTT, ZeroMQ, CoAP and Nanomsg. But after
involving other parameters (simplicity, broker,...) we can only talk about ZeroMQ and Nanomsg. Both of these protocols
are cautious to use resources and never make big concerns around this parameter.
