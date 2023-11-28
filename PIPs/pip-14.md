---
pip: 14
title: Adding more details in agent hello and structured value
author: Javad Rajabzadeh <ja7ad@live.com>
status: Accepted
category: Network
created: 2023-11-28
---

## Abstract

The proposal suggests enhancing the structure of the "Agent" field in the Peer details by introducing a more detailed and standardized format. The current implementation provides only the node name and version, while the proposed update aims to include additional information such as the type of agent (GUI or DAEMON), operating system, and architecture. This structured approach will offer a more comprehensive view of the agent details.

![Peer Information](../assets/pip-14/agent.png)

## Motivation

The motivation behind this proposal is to provide a richer set of information within the "Agent" field. The current format lacks essential details that could be valuable for various purposes, including monitoring, debugging, and compatibility checks. By incorporating information such as agent type, operating system, and architecture, we aim to improve the overall usefulness of the "Agent" field.

## Specification

The updated **"Agent"** field will follow a structured key-value format, separated by slashes **("/")**. The proposed format is as follows:

```go
func Agent() string {
    return fmt.Sprintf("node=pactus/version=%s/type={GUI or DAEMON}/os=%s/arch=%s", Version(), runtime.GOOS, runtime.GOARCH)
}
```

- node: The name of the node.
- version: The version of the node.
- type: The type of the agent, indicating whether it is a GUI or DAEMON.
- os: The operating system on which the agent is running.
- architecture: The architecture of the system where the agent is deployed.
- and more **key=value**
