---
pip: 13
title: Aligning Block Versions with Node Versions for Enhanced Network Security
author: Javad Rajabzadeh <ja7ad@live.com
status: Draft
category: Core
created: 2023-11-26
---

## Abstract

This improvement proposal addresses the need for ensuring network integrity and security by introducing dynamic block versioning based on the node version during the block commitment process in our blockchain implementation. The primary goal is to prevent older nodes from creating and committing new blocks, compelling node operators to upgrade to the latest version. By tying the block version to the major and minor version of the running node, this proposal promotes a more secure and consistent network environment. The abstract outlines the problem statement, the proposed solution, implementation details, and the anticipated benefits of this enhancement.

## Motivation

In the ever-evolving landscape of blockchain technology, ensuring the continuous improvement and security of the network is paramount. The motivation behind this proposal stems from the need to address a critical challenge: the presence of outdated nodes in the network. These nodes, running on older versions, pose a potential threat to the overall integrity of the blockchain by lacking essential updates and security enhancements.

By introducing dynamic block versioning based on the node version during the block commitment process, we aim to create a compelling reason for node operators to keep their systems up-to-date. This proactive approach not only minimizes the risk of vulnerabilities associated with outdated nodes but also fosters a more secure and consistent network environment.

This enhancement serves as a pivotal step towards establishing a robust foundation for the blockchain, aligning the network's versioning strategy with the evolving nature of the underlying technology. Through this motivation, we strive to fortify the blockchain ecosystem, ensuring that all nodes contribute to a resilient and up-to-date network.

## Specification

Modify the existing `headerData` structure to include a function for setting the block version based on the node version. The setBlockVersion function will be responsible for parsing the node version and updating the block version accordingly.

```go
type headerData struct {
    Version         uint16
    UnixTime        uint32
    PrevBlockHash   hash.Hash
    StateRoot       hash.Hash
    SortitionSeed   sortition.VerifiableSeed
    ProposerAddress crypto.Address
}

func (header *headerData) setBlockVersion(nodeVersion string) {
    major, minor, _ := parseNodeVersion(nodeVersion)
    header.Version = uint16((major * 100) + minor)
}
```

Ensure that the `setBlockVersion` function is invoked during the block commitment process to set the block version based on the running node's version. For example, if the node version is "1.17.1," the block version will be set to 117.

Update relevant documentation to include information about the dynamic block versioning mechanism. Clearly communicate the format in which the node version translates into the block version, such as `major * 100 + minor`.

Thoroughly test the modified block header structure and versioning logic to ensure compatibility and correctness across different node versions. Implement test cases to cover various scenarios, including successful version parsing and forced upgrades.

## Backward Compatibility

Consider any backward compatibility concerns and implement measures to minimize disruptions for existing node operators during the transition to the new versioning system.

These specifications provide detailed steps for implementing dynamic block versioning based on the node version, with the Version field type updated to `uint16`.
