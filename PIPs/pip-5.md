---
pip: 5
title: Adding Different HRP For Validator, Account And Contract Address
status: Withdrawn
type: Standards Track
author: Kayhan Alizadeh <kehiiiiya@gmail.com>
created: 2023-08-27
---

## Abstract

This proposal suggests adding a specific prefix to different address types in Pactus, such as `validator` and `account`, to make their roles more understandable. 

## Motivation

Currently, Pactus addresses are identified by a `pc` prefix, regardless of their type. This makes it hard for both humans and machines to identify the role of each address, whether it belongs to an `account`, `validator`, or `contract`. By adding appropriate prefixes, we can quickly and easily identify the purpose of each address. For example:

## Specification

To achieve this, we can define `3` prefix options for the current address types: `pv` for validators, `pc` for contracts, and `pa` for accounts. All addresses must have the correct prefix to be considered valid in Pactus. Additionally, we should consider the version number after the prefix to be related to the specific address type.
 
- Account:   `pa1puc5zza3hnp2tcf6r5n8zz0mwcjhqlxtejnjkzv`
- Validator: `pv1p8wqgmagsrzn0nr26weg6wekqtu2mc6uw72k04a`
- Contract:  `pc1pdw5fda6r757q780xvtsxhfls24vekrfqmddqrs`

Furthermore, any possible future address types must follow the same rule and have their own prefix.
