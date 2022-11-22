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

1. Cover any penalties that may result from the flags applied by the log detection system.
2. Leverage the known bias of humans for avoiding known losses (loss aversion). In other words, losing money is known to be a stronger deterrent than not earning the full potential reward.
3. Increase the cost of takeover attacks where a single operator floods the network with a huge number of nodes feeding from the same hardware resources.
4. Increase the commitment of node operators to the Saturn network. 
5. Deter operators from leaving the network and joining with a new identity, relieving the previous identity from penalties and the previous bad reputation.

Thus, in short, collateral in the Saturn network serves two main goals - deter undesired behavior and increase alignment of participants with the long-term success of the network. This fact is key - collateral is not meant to just cover potential penalties. Instead, it needs to provide an additional layer of commitment and security.

## Main mechanisms

:::info
:hammer: WIP
:::

In this section, we will discuss the processes to enable collateral and how operators will interact with it. Note that are leaving the processes general enough to allow flexibility on the implementation. In particular, we will discuss three main mechanisms that are closely tied to collateral:

1. Operator onboarding
2. Slashing due to misbehavior
3. Operator termination and renewal

### Onboarding

When an operator wishes to join Saturn, they will have to go through the following process:

1. Operator states their resources and expected level of service. This includes stating their upload bandwidth, their available cache size, and the minimum time commitment. 
2. Saturn estimates their expected earnings based on the current network performance, reward pool, and the operators' stated performance metrics.
3. Saturn uses the expected earnings to provide the collateral amount for the operator.
4. Operator sends the collateral amount to Saturn.
5. Saturn starts sending retrieval requests to the operator.

Note that we are asking the operators to state their own performance metrics, which means we are trusting their "word" in order to compute collateral. This may seem to be lead to a phenomenon where nodes state the minimum requirements in order to pay less collateral. However, this is a double-edged sword because we can always compare the reported metrics with the actual services being delivered. If an operator reports a 10Gbps upload speed, we can flag the operator when they suddenly serve 12 Gbps. On the other hand, if an operator overpromises, they will have to pay a higher collateral while seeing their rewards adjust to actual performance delivered.

Another important consideration is the time commitment. Why do we need a time commitment? The reason is twofold:
1. Having an upfront commitment of operators (and consequences in case the commitment is broken) leads to a more stable and predictable service.
2. Having an "end-date" to the service allow us to reassess collateral calculations as the traffic and expected rewards change.

:::warning
:warning: Can we think of any issues/problems with asking operators to state a time commitment and slashing them if the commitment is not met?
:::

Finally, we note that the node operator only starts receiving requests once the funds are sent. This is to avoid fraudulent operators joining the network to disrupt operations without "staking" some money. If we allow operators to receive requests before the collateral is committed, then there is a clear opening for these type of behavior.

### Slashing

Collateral will be slashed in two distinct occasions:
1. When the node misbehaves and is flagged by the [log detection system](/WihFXzN9QteSwIxHW5zKeQ).
2. When the node breaks the agreed service upon onboarding (e.g., leaving the network earlier or consistently performing below the metrics stated).

In the first occasion, we apply the [penalty multiplier](/MqxcRhVdSi2txAKW7pCh5Q#Penalty-multiplier) designed previously. Recall that it is a multiplier of the average rewards of the operator. In the second occasion, we don't have a concrete proposal on the optimal amount, so some analysis and simulation is required.

:::info
:hammer: We still need to specify how much we should slash in case nodes underperform when compared with their commitment upon onboarding. And in which situations we say nodes are not delivering on their committed service.
:::

In both cases, a certain amount of the collateral is removed from the operator's balance. Now, we have two options in case slashing:
1. We stop requests until the operator adds more funds to their collateral balance to make up for the loss. This is the safest approach, but it has two main drawbacks, namely, it will impact service since requests need to be routed to other operators, and it will penalize even more the honest operators that are flagged by the log detection system (we always expect some level of False Positives).
2. We use the future rewards to replenish the collateral balance, but we continue to send requests to the operator. This is less penalizing for honest nodes, but it may be a problem for misbehaving nodes that are not fulfilling a good level of service.

:::warning
:warning: what is the best approach for replenishing collateral after slashing? Can we mitigate loss of service while avoiding customer experience to be hurt by misbehaving operators?
:::

Another important question is what happens to slashed funds? We have two options:

1. "Burn" the funds. We cannot literally burn the tokens because they will be FIL tokens. However, we can simulate this concept in FVM by sending them to a dead address not controlled by anyone.
2. Send the funds back to the main reward pool. We can interpret this as a refund to clients since the operation will be in part funded by the misbehaving operators.

:::warning
:warning: what is the best way to deal with the slashed funds?
:::

### Renewal and termination

During onboarding, the node operator stated the time period they were expected to participate in the Saturn network.  Once that period finishes, the node operator has two options - terminate or renew. Termination means that the node will exit the network, stop receiving requests and rewards and will receive the collateral back. Renewal means that the node will continue in the network, continue to serve requests and receive rewards and the collateral will be updated. This update may require additional funds to be added in the case where the network rewards have increased since the time when the operator first onboarded.

More concretely, every time an operator reaches the end of commitment period, the following process would be executed:

1. Saturn recalculates the new collateral amount
2. Saturn sends a notification to the operator warning that the commitment period has ended and informing them of the new collateral amount.
3. Operator decides whether they wish to renew or terminate:
   1. If the operator wishes to terminate:
      - They can withdraw the funds without penalties.
    2. If the operator wishes to renew:
      - They can update their time commitment - if nothing is stated here, we assume the same period
      - They will update the collateral (add more if the new requirement is higher)
4. After a predefined time (TBD), Saturn will check collateral:
   - If the collateral is smaller than the required, Saturn will stop sending requests and no more rewards will be paid.
   - If the collateral is higher of equal to the required, Saturn will continue to send request to the operator and distributing rewards

Note that, unless the collateral requirement changes, the default outcome (i.e. if the operator does nothing) will be a renewal for the same period of commitment. This is an important point as it implies the collateral amount should be biased to avoid changes. 

Another consideration is how much time we give operators to decide and execute on the terminations/renewals. If we give too little time, operators won't be able to make a decision and will fall under the default option (which can be either a renewal or a termination). If it too much time, then we allow operators that are exiting the network to extract additional rewards without updating their collateral.

## Collateral amount

:::info
:hammer: WIP
:::

