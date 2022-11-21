---
title: Saturn collateral - design document
tags: Saturn aliens, Retrievals
description: Specification of the collateral mechanism for Saturn's L1 node operators
breaks: false
---

# Collateral for Saturn's L1 nodes - design document

[![hackmd-github-sync-badge](https://hackmd.io/xZGGNN_ZTyewqwYrgLuisA/badge)](https://hackmd.io/xZGGNN_ZTyewqwYrgLuisA)

#### Maria Silva, November 2022

In this report, we detail how the collateral mechanism for Saturn's L1 node operators functions and the principles underlying the design. We also provide more details about how the collateral value is estimated.

## Motivation and principles

Saturn is a decentralized network of nodes that work together to deliver online content fast. This means that anyone that meets the hardware requirements can join, contribute resources and collect payments from that contribution. This permissionless nature of the system means that the network is open to a set of attacks that need to be mitigated with the right incentive design.

One of those design choices is the application of [penalties](/MqxcRhVdSi2txAKW7pCh5Q#Penalties) when a node operator is flagged by the [log detection system](/WihFXzN9QteSwIxHW5zKeQ). In the first iteration, we assumed that operators would not have to submit collateral to join the network and, instead, we would deduct penalties from future earnings. This choice was motivated by the desire to reduce entry barriers and instigate adoption. There was also the understanding that this choice would be reviewed after the launch date.

Since then, the network of L1 operators in Saturn has seen a significant adoption and, as such, we are in the right moment to consider adding a collateral mechanism. Concretely, such a mechanism is meant to fulfill the following functions:

1. Cover any penalties that may result from the flags applied by the log detection system
2. Leverage the known bias of humans for avoiding known losses (loss aversion). In other words, losing money is known to be a stronger deterrent than not earning the full potential reward.
3. Increase the cost of takeover attacks where a single operator floods the network with a huge number of nodes feeding from the same hardware resources.
4. Increase the commitment of node operators to the Saturn network. 

Thus, in short, collateral in the Saturn network serves two main goals - deter undesired behavior and increase alignment of participants with the long-term success of the network. This fact is key - collateral is not meant to just cover potential penalties. Instead, it needs to provide an additional layer of commitment and security.

## Main mechanisms

:::info
:hammer: WIP
:::

## Collateral amount

:::info
:hammer: WIP
:::

