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

This document explains the consumptional fee.
The consumptional fee calculates based on the amount of data each address consumes daily.

## Motivation

Some users want to find ways to pay lower fees to the network.
These users usually don’t mind how long it takes for their transactions to be confirmed.
By introducing the consumption fee, we can allow transactions with zero or low fees to be processed in the network.
However, these transactions may take longer than usual to be confirmed.

## Specification

Each validator can calculate the minimum fee for every transaction they receive using this formula:

$$
\text{min_fee} = \text{fixed_fee} + \text{consumptional_fee}
$$

Validators reject transactions with fees lower than the minimum fee.
They will keep transactions with higher fees in their transaction pool and later include them in the proposed blocks.

### Fixed Fee

The fixed fee is a constant fee applied to each transaction, regardless of its size or type.
This parameter is part of the node configuration, allowing each validator to set their preferred value.

### Consumptional Fee

The consumptional Fee calculates as follow:

$$
\text{consumptional_fee} = ( \text{coefficient} \times \text{consumption} \times \text{unit_price} )
$$

Let's explain the parameters:

#### Consumption

To understand the Consumptional Fee Model, we first need to define consumption.

Transactions are sequences of bytes that validators decode, process, and store in their local database.
Consumption is defined as the number of bytes stored over the last 8640 blocks [^1]
for a specific account that signed a transactions.

#### Coefficient

The coefficient is a unitless number that starts at zero and grows naturally: $0, 1, 2, 3, \dots $

The coefficient would be calculated as follows:

$$
\text{coefficient} = \lfloor \frac{\text{consumption}}{\text{daily_limit}} \rfloor
$$

In this formula [^2], the daily limit is the number of bytes an account can send each day without paying a fee.
This parameter is part of the node configuration, allowing each validator to set their preferred value.

The only exception here is the account that broadcasts its first transaction.
The coefficient for an account that sends its first transaction is always set to `1`.

#### Unit Price

The unit price would define the fee per byte in PAC.
This parameter is part of the node configuration, allowing each validator to set their preferred value.

### Configuration

All parameters for calculating the fee are configurable.
However, we recommend the following configurations:

For most validators, we suggest setting the daily limit to `0 bytes` and the fixed fee to `0.01 PAC`.
This configuration eliminates the consumption fee, meaning these validators will only apply the fixed fee.

For validators with good resources, we recommend setting the daily limit to `280 bytes`,
the unit price to `0.000005 PAC`, and the fixed fee to `0 PAC`.
This allows users to send almost up to 5 free or low-fee transactions,
but they will need to wait for these validators to enter the committee and propose the block.
This way, the Pactus blockchain can support zero-fee transactions.

### Implementation Considerations

There are some challenges in implementing the Consumptional Fee Model:

#### Calculating Consumption

To calculate consumption, we can define a map that associates an address with
the total size of transactions stored in the blockchain over the last 8640 blocks.
When a new block is committed, we update this map by iterating over all transactions in the block and
increasing the value for each address by the size of its transactions.
Simultaneously, the block from 8640 blocks ago would be retrieved,
and the value for each address would be decreased by the size of its transactions.

#### New Account Detection

To determine if an account is new and hasn't sent any transactions yet,
we can check if its public key is indexed. If the public key is not indexed,
it indicates that the account is sending a transaction for the first time.

#### Withdraw fee

Withdrawal transactions are issued and signed by validators,
and the fee for them can be calculated based on the Consumptional Fee model.

## References

[^1]: Based on the consensus parameters, the time to reach a block is 10 seconds,
    and 8640 blocks is approximately one day.

[^2]: The symbol $\lfloor x \rfloor$ denotes the **floor function**,
    which rounds down $x$ to the nearest whole number.
