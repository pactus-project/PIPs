---
pip: 14
title: Client Agent Standard
author: Javad Rajabzadeh <ja7ad@live.com>
status: Final
type: Standards Track
category: Networking
created: 2023-11-28
---

## Abstract

This proposal suggests enhancing the structure of the client **"Agent"** by introducing a more detailed and standardized format.

## Motivation

The current implementation provides only the agent's version, while the proposed update aims to include additional information such as the application name, operating system, and architecture. This structured approach will offer a more comprehensive view of the agent details.

## Specification

The client agent will contain **key=value** fields separated by slashes **("/")**, and all key-values are in lowercase. The proposed keys are:

- node: The application name of the agent.
- node-version: The version of the agent, following the [semantic version 2](https://semver.org/spec/v2.0.0.html) standard.
- protocol-version: This is the same as the latest **block version** supported by the agent.
- os: The operating system on which the agent is running.
- arch: The architecture of the system where the agent is deployed.

## Example

```text
node=pactus-gui/node-version=v1.2.3/protocol-version=1/os=windows/arch=amd64

node=pactus-daemon/node-version=v1.2.3/protocol-version=1/os=linux/arch=arm
```
