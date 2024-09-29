---
pip: 33
title: New Address Type: Lock Account Address
author: Mr. HoDL (@Mr-HoDL58)
status: Draft
type: Standards Track
category: Core
created: 2024-09-29
---

## Abstract

This proposal outlines the introduction of a new address type known as the "Lock Account Address." The purpose 
of this new feature is to offer users a mechanism to lock their assets for a specified period, thereby 
promoting better financial management within our platform.

## Motivation

The Lock Account Address will facilitate a unique type of transaction called the "Lock Transaction." This 
transaction is a combination of bonding and unbonding, governed by specific date and time parameters. 
By implementing this mechanism, The project and its users can secure their funds over defined periods while 
still being able to withdraw portions of their assets when unlocked. This would serve as an alternative to 
PIP-32 by offering another solution to the unlocked reserve coins.

## Specification

Addition of new address type `Lock Account Address`

### Lock Command Structure

The Lock Time Transaction will follow the command structure outlined below:

`tx lock <from> <to> <amount> <lockdays> <unlockdays>`

#### Parameters

Lockdays: This parameter represents the total amount of time the coins will be locked.
Unlockdays: This signifies the time interval between each unlock.

The formula for calculating the amount eligible for unlocking is given by:

`locked_amount / lockdays * unlockdays = X per unlockdays`

#### Example

For instance, if a user locks 100 coins for 100 days, with an unlock period of 1 day, the calculation would be:

`100 coins locked / (100 days locked * 1 day) = 1 coin per day`

The user will be able to unlock 1 coin every day until the locked amount is depleted.

### Unlock Transaction Command Structure

The Unlock Transaction, which is used to withdraw the balance that has been unlocked, will follow this structure:

 `tx unlock <from> <to> <amount/available>`

The "amount/available" to unlock will be automatically determined when the transaction is called, ensuring users only withdraw the amounts that have matured based on the lock parameters.

### Additional Parameters

To provide users with greater flexibility and control, the Lock Time Transaction must include at least one lock parameter and one unlock parameter. Below are the definitions of the additional time parameters:

Lockdays:
    `-lkdays`: Equivalent to 8640 Blocks
    `-lkhours`: Equivalent to 360 Blocks
    `-lkmins`: Equivalent to 6 Blocks

Unlockdays:
    -uldays: Equivalent to specified days
    -ulhour: Equivalent to specified hours
    -ulmins: Equivalent to specified minutes


