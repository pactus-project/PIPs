---
pip: 24
title: Snap mode synchronization blockchain data
author: Javad Rajabzadeh (@ja7ad)
status: Draft
type: Standards
category: Network
created: 08-05-2024
---

## Abstract

The proposed Snap mode synchronization for Pactus blockchain offers a streamlined approach to syncing blockchain data. By enabling users to download pre-packaged blockchain data from a centralized storage location via unique links with checksum hashes, this feature significantly reduces syncing time and resource usage. It enhances network accessibility, scalability, and security without compromising backward compatibility.

## Motivation

Currently, syncing full blockchain data from P2P networks can be time-consuming and resource-intensive, especially for new node operators or users with limited bandwidth. This poses a significant barrier to entry for individuals looking to participate in the Pactus blockchain network. By introducing Snap mode synchronization, we aim to address this issue by providing a more efficient and convenient method for users to obtain blockchain data.

The motivation behind this proposal is to:

1. Improve accessibility: Simplify the process of setting up a new node by offering a centralized download link for blockchain data, making it easier for users to join the Pactus network.

2. Reduce syncing time: By downloading pre-packaged blockchain data from a centralized storage location, users can significantly reduce the time required to synchronize their node with the network.

3. Optimize resource utilization: Minimize the strain on network resources and bandwidth by offering a centralized download option, thereby improving overall network efficiency and scalability.

## Specification

The Snap mode synchronization feature will be implemented as follows:

1. Centralized storage: A centralized storage location will be set up to host original blockchain data files.

2. Checksum hash generation: Alongside the download link, a checksum hash will be provided to ensure data integrity during the download process.

3. Node setup command: Users can initiate the synchronization process by running the command `./pactus-daemon import` start to download last blockchain data very fast from the server closest to you.

4. Data verification: Upon completion of the download every blockchain data, the node will verify the integrity of the downloaded data using the provided checksum hash.

5. Synchronization: The node will import the downloaded blockchain data and synchronize with the Pactus network.

### Example

Example metadata of blockchain data:

```json
[
    {
        "filename": "008149.ldb",
        "path": "store.db/008149.ldb",
        "hash": "07cd0dbdc4f6d0f677e0f2f3c47b9f4d6c112f507198a84ac38ed5389f5de0b2"
    }
]
```

## Backward Compatibility

This improvement proposal maintains backward compatibility with existing Pactus blockchain infrastructure and protocols. Users who prefer to sync data via the traditional P2P network can continue to do so without any disruption. The Snap mode synchronization feature provides an alternative method for syncing blockchain data and does not require any changes to the underlying blockchain protocol.

## Security

To ensure the security of the Snap mode synchronization feature, the following measures will be implemented:

1. Checksum verification: Users will verify the integrity of the downloaded data using the provided checksum hash before importing it into their node.

2. Centralized storage security: The centralized storage location will be secured using industry-standard security practices to prevent data breaches and unauthorized access.

3. Regular updates: The blockchain data stored in the centralized storage will be regularly updated to ensure that users have access to the latest blockchain data.


By implementing these security measures, users can trust the integrity and authenticity of the blockchain data obtained through the Snap mode synchronization feature.
