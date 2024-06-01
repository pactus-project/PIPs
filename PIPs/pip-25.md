---
pip: 25
title: Dynamic fees structure
author: Javad Rajabzadeh (@b00f)
status: Draft
type: Standards
category: Core
created: 1-06-2024
---

## Abstract

A dynamic fee structure adjusts the required transaction fees and burn amounts in response to real-time network conditions. This approach helps deter spam transactions by making it more expensive to flood the network during times of high activity

### Motivation

The Pactus blockchain, which operates on a Proof of Stake (PoS) committee-based consensus protocol, faces the challenge of spam attacks that can clog the network and degrade performance. Spam transactions can flood the blockchain, causing delays and increasing the cost for legitimate users. To address this issue, we propose the implementation of a dynamic fee structure that adjusts transaction fees and burn amounts based on real-time network conditions. This adaptive mechanism aims to:

1. Deter spam transactions by making it economically unfeasible to flood the network.
2. Ensure smooth operation of the blockchain during periods of high and low activity.
3. Maintain fairness and transparency in fee adjustments for all users.

### Specification

#### 1. **Monitoring Network Conditions**
- **Transaction Volume**: Track the number of transactions per block and per unit of time.
- **Network Congestion**: Measure the average time it takes for a transaction to be included in a block.
- **Block Utilization**: Monitor the average size and utilization of blocks (e.g., percentage of block capacity used).

#### 2. **Fee Adjustment Algorithms**
- Define algorithms that adjust transaction fees and burn amounts dynamically. The fees will be calculated using the following formula:

\[ \text{Adjusted Fee} = \text{Base Fee} \times (1 + \alpha \times \frac{\text{Current Transaction Volume}}{\text{Average Transaction Volume}}) \]

  - **Base Fee**: Standard fee under normal conditions.
  - **\(\alpha\)**: Coefficient determining fee sensitivity to volume changes.
  - **Current Transaction Volume**: Number of transactions in the current observation window.
  - **Average Transaction Volume**: Historical average transactions in a typical observation window.

#### 3. **Real-Time Adjustment Mechanisms**
- Use a sliding window of recent blocks (e.g., last 100 blocks) to calculate average network conditions.
- Implement predictive analytics to forecast network congestion and adjust fees preemptively.
- Continuously update fees based on the latest network data, creating a feedback loop for maintaining optimal fees.

#### 4. **Core Protocol Integration**
- Modify the transaction validation and block creation process to include the dynamic fee adjustment logic.
- Ensure that all nodes in the network can independently verify and enforce the adjusted fees.

#### 5. **User Interface Updates**
- Update wallet software and other user interfaces to display current transaction fees and burn amounts.
- Provide users with real-time information on how fees are calculated and adjusted.

### Backward Compatibility

- **Seamless Transition**: Ensure the dynamic fee structure is backward compatible with existing transactions and network operations. Users should not need to change their current practices, and all existing functionalities should remain intact.
- **Legacy Support**: Ensure that legacy transactions continue to function without modification. The system will integrate with the current protocol without requiring significant changes to the existing infrastructure.
- **Comprehensive Documentation**: Provide comprehensive documentation and support to help users and developers understand and adapt to the new fee structure.

### Security

- **Manipulation Resistance**: Implement robust algorithms and validation mechanisms to prevent manipulation of the fee adjustment process. Ensure that no single entity can influence the dynamic fee calculations unfairly.
- **Data Integrity**: Secure the data collection and monitoring tools to ensure the accuracy and integrity of the network metrics used for fee adjustments.
- **Protocol Security**: Conduct thorough security reviews of the core protocol modifications to identify and mitigate potential vulnerabilities.
- **Economic Security**: Carefully calibrate the fee adjustment algorithms to avoid creating economic imbalances. Ensure that the cost of legitimate transactions remains reasonable while effectively deterring spam.
- **Transparency and Accountability**: Maintain transparency in the fee adjustment process by making the algorithms and data publicly available for review. Establish accountability mechanisms to address any issues or concerns raised by the community.
