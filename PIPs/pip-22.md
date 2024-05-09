---
pip: 22
title: Agent Node Defination
author: Nagaraj (@ragnarok87)
status: Accepted
type: Standards
category: Interface
created: 29-01-2024
requires: 14
---

## Abstract

The purpose of this proposal is to redefine the node field as "application type" instead of "application name" in the agent string.

## Motivation

Based on [PIP14](./pip-14.md), the node field is defined as "The application name of the agent." There are two problems with this definition:

* Depending on the operating system, the node field can change, e.g., `pactus-gui` & `pactus-gui.exe`.
* Some users rename the application, for example, to `pdeamon`.

## Specification

This proposal suggests defining the node field as the application type of the agent, as defined below:

1. `daemon`: If the client agent is a CLI or Daemon application.
2. `gui`: If the client agent is a GUI application.

## Security Considerations

The implementation of this time check feature should not compromise security.