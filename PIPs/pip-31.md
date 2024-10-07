---
pip: 31
title: Consumptional Fee Model
description: Transaction Fee Based on Data Consumption
author: Pactus Development Team <info@pactus.org>
discussion-no: 172
status: Draft
type: Standards Track
category: Core
created: 08-08-2024
---

## Abstract

This document proposes calculating the fee based on the amount of data each account consumes daily.

## Specification

The transaction fee can be determined based on either the Consumption Fee.
Validators can drop transactions with lower fees,
but transactions with higher fees are accepted and kept in the transaction pool.

### Consumptional Fee

Each validator can independently calculate the fee for each transaction based on the following formula:

$$
\text{fee} = \text{fixed_fee} + ( \text{coefficient} \times \text{consumption} \times \text{unit_price} )
$$

Let's explain the parameters:

#### Fixed Fee

The `fixed_fee` is a constant fee applied to each transaction, regardless of its size.
This parameter would be part of the node configuration, allowing each validator to set their preferred value.
The default value for `fixed_fee` is proposed to be set to zero.

#### Consumption

To understand the Consumptional Fee Model, we first need to define consumption.

Transactions are sequences of bytes that are decoded, processed, and stored by validators.
Consumption is defined as the number of bytes stored over the last 8640 blocks [^1] for a specific account.

#### Coefficient

The coefficient is a unitless number that starts at zero and grows exponentially: $0, 1, 2, 4, 8, \dots $

The coefficient would be calculated as follows:

$$
n = \frac{\text{consumption}}{\text{daily_limit}}
$$

$$
\displaylines{\text{coefficient} = \begin{cases}  0 & \text{if } n = 0 \\ 2^{n-1} & \text{if } n \geq 1 \end{cases}
}
$$

In this model, the daily_limit is the number of bytes an account can send each day without paying a fee.
This parameter would be part of the node configuration, allowing each validator to set their preferred value.

The default value for `daily_limit` is proposed to be **300 bytes**

#### Unit Price

The unit_price would define the fee per byte in PAC. This parameter would be part of the node configuration,
allowing each validator to set their preferred value.

The default value for `unit_price` is proposed to be **0.0001 PAC**.

### Account Creation Fee

Each account needs to pay a `fixed_fee` the first time, after which a consumptional fee is applied.

### Implementation Considerations

There are some challenges in implementing the Consumptional Fee Model:

#### Calculating Consumption

To calculate consumption, we can define a map that associates an address with
the total size of transactions stored in the blockchain over the last 8640 blocks.
When a new block is committed, we update this map by iterating over all transactions in the block and
increasing the value for each address by the size of its transactions.
Simultaneously, the block from 8640 blocks ago would be retrieved,
and the value for each address would be decreased by the size of its transactions.

For store this details in map we **don't have** overhead for 8640 blocks (`map[crypto.Address]uint16`):

- **Key size**: 21 bytes (account address)
- **Value size**: 2 bytes (`uint16`)
- **Overhead**: Estimated at 8-16 bytes per entry for pointers, hash management, and bucket arrays

The total size is computed by multiplying the size of each item (sum of key size, value size, and overhead) by
the number of items.

$$
\[
\text{Total Size} = (\text{key size} + \text{value size} + \text{overhead}) \times \text{number of items}
\]
$$

For the first case:

$$
\[
\text{Total Size} = (21 + 2 + 8) \times 8640 = 259,200 \, \text{bytes} \approx 260 \, \text{KB}
\]
$$

For the second case (with a larger overhead):

$$
\[
\text{Total Size} = (21 + 2 + 16) \times 8640 = 345,600 \, \text{bytes} \approx 346 \, \text{KB}
\]
$$

So, the map size is approximately **260KB to 346KB**.

#### New Account Detection

To determine if an account is new and hasn't sent any transactions yet,
we can check if its public key is indexed. If the public key is not indexed,
it indicates that the account is sending a transaction for the first time,
and the account creation fee should be applied.

#### Withdraw fee

Withdrawal transactions are issued and signed by validators,
and the fee for them can be calculated based on the Consumptional Fee model.

## References

[^1]: Based on the consensus parameters, the time to reach a block is 10 seconds,
    and 8640 blocks is approximately one day.
