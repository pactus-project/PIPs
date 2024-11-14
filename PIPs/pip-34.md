---
pip: 34
title: Fee-Based Prioritization with Weighted Random Selection
author: Javad Rajabzadeh (@Ja7ad), Mohammad Allahbakhsh <allahbakhsh@gmail.com>
status: Draft
type: Informational
category: Core
created: 2024-11-02
requires: 31
---

## Abstract

This proposal introduces an enhancement to the transaction pool management system in Pactus blockchain, aiming to optimize
transaction selection for block inclusion when the transaction pool size exceeds the block capacity. The method focuses on
prioritizing transactions by fee while maintaining fairness through a weighted random selection mechanism.

## Motivation

Efficient transaction selection is vital for maintaining network performance, user satisfaction, and economic balance in the
Pactus blockchain. When the transaction pool holds more transactions than can fit in a block, a smart selection strategy is
necessary to balance priority and fairness while ensuring optimal block composition.

## Specification

The weighted random selection algorithm is designed to be applied in scenarios where the transaction pool exceeds the block
size limit ($block size < len(tx pool)$) and not all transactions can be included in the block. This situation often occurs
during high network activity when the transaction pool contains more pending transactions than can fit into a single block.

### Key Concepts

1. **Insertion Sort for Transaction Management**: Keeps the transaction pool sorted as new transactions are validated and added,
ensuring efficient access during block proposal.
2. **Weighted Random Selection for Block Proposal**: Prioritizes transactions based on fees using a weighted random selection method,
providing higher chances of selection to higher-fee transactions while still allowing lower-fee ones to be considered.
3. **Array Construction for Block Transactions**: Reserves a portion of the block for specific transaction types (e.g., reward,
sortition, unbond), and fills the remaining space using the weighted random selection algorithm.

### Insertion Sort for Transaction Management

- **Objective**: Maintain an efficiently sorted transaction pool.
- **Method**:
  
  1. Validate incoming transactions.
  2. Insert validated transactions into the pool in the correct order using insertion sort, prioritizing based on fees or other criteria.

### Weighted Random Selection Algorithm

- **Objective**: Ensure that transactions are selected based on fees with some randomness to allow diversity.
- **Steps**:
  
  - **Include Essential Transactions**:
    
    - Directly include transactions of type **reward**, **sortition**, and **unbond**.
    - Deduct their count from `block_size` to determine the remaining slots.
  
  - **Determine Remaining Capacity**:
    
    - Let $M$ be the initial `block_size`.
    - Let $N$ be the number of highest-fee transactions included directly.
    - Let $O$ represent the number of **sortition** and **unbond** transactions.
    - Let $1$ be the block reward transaction.
      
    $$
    M_{\text{remaining}} = (M - N - O) - 1
    $$

  - **Assign Virtual Fees**:
    
    - Assign a virtual fee of $f_{\text{min}} / 2$ to zero-fee transactions to include them in the weighted selection.
  
  - **Calculate Total Fee Sum**:
    
    - Compute the sum of fees for all remaining transactions:
      
    $$
    \text{Total fee sum} = \sum_{i=1}^{w} f_i
    $$

  - **Calculate Weights**:
    
    - Determine the weight for each transaction $i$:
      
    $$
    w_i = \frac{f_i}{\text{Total fee sum}}
    $$

  - **Select Transactions Randomly**:
    
    - Select $M_{\text{remaining}}$ transactions using a weighted random approach, ensuring higher-fee transactions are more
    likely to be chosen while giving lower-fee transactions a chance.

## Example Test Case

| **Transaction ID** | **Type**      | **Fee**  |
|---------------------|---------------|----------|
| tx4                 | Unbond        | -        |
| tx5                 | Sortition     | -        |
| tx6                 | Sortition     | -        |
| tx3                 | Transfer      | 0.0      |
| tx9                 | Bond          | 0.0      |
| tx12                | Transfer      | 0.0      |
| tx2                 | Bond          | 0.0002   |
| tx1                 | Transfer      | 0.001    |
| tx7                 | Transfer      | 0.0023   |
| tx8                 | Transfer      | 0.00337  |
| tx10                | Bond          | 0.01     |
| tx11                | Transfer      | 0.01     |

### Analysis for Block Inclusion

- **Block Size**: 10 transactions.
- **Initial Inclusion**:
  
  - Include `tx4`, `tx5`, and `tx6` (unbond and sortition).
  - Remaining slots: $10 - 3 = 7$.

### Next Steps

- Include highest-fee transactions: `tx10` and `tx11` (0.01).
- Remaining slots: $7 - 2 = 5$.

### Calculate Total Fee Sum

Sum of fees: $\(0.001 + 0.0002 + 0.0023 + 0.00337 + 0.0001 \times 3 = 0.00717\)$

### Calculate Weights

Calculate the weight for each transaction $\( i \)$:

- $\( w_1 = \frac{0.001}{0.00717} \)$
- $\( w_2 = \frac{0.0002}{0.00717} \)$
- $\( w_3 = \frac{0.0001}{0.00717} \)$
- $\( w_4 = \frac{0.0023}{0.00717} \)$
- $\( w_5 = \frac{0.00337}{0.00717} \)$
- $\( w_6 = \frac{0.0001}{0.00717} \)$
- $\( w_{7} = \frac{0.0001}{0.00717} \)$

### Weight Calculation

Calculate the weight for each remaining transaction and perform a weighted random selection to fill the remaining slots.

This approach ensures a balanced block composition, maintaining prioritization by fees while allowing for fairness and diversity
in transaction selection.
