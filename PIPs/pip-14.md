---
pip: 14
title: Client agent standard
author: Javad Rajabzadeh <ja7ad@live.com>
status: Accepted
category: Network
created: 2023-11-28
---

## Abstract

The proposal suggests enhancing the structure of the client **"Agent"** by introducing a more detailed and standardized format.

## Motivation

The current implementation provides only the node name and version, while the proposed update aims to include additional information such as
the type of agent (GUI or CLI), operating system, and architecture. This structured approach will offer a more comprehensive view of the agent details.

## Specification

The client agent will contain **key=value** fields that separates by slashes **("/")**, all key-values are lower case. The proposed keys are:

- node: The name of the node.
- node-version: The version follow is [semantic version 2](https://semver.org/spec/v2.0.0.html) of the node.
- protocol-version: It same as latest **block version** that node support
- os: The operating system on which the agent is running.
- arch: The architecture of the system where the agent is deployed.

## Example

```text
node=pactus-gui/node-version=v1.2.3/protocol-version=1/os=windows/arch=amd64

node=pactus-daemon/node-version=v1.2.3/protocol-version=1/os=linux/arch=arm
```