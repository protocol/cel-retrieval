---
title: Saturn aliens - CEL Paris colo 07-2022
tags: Saturn aliens
description: Slides for supporting the discussion about the Saturn Aliens project with CEL
---

# Reward distribution for Saturn

[![hackmd-github-sync-badge](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q/badge)](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q)

#### Maria Silva, August 2022

###### tags: `Saturn aliens`

**TLDR:** TBD

## Retrieval markets and Saturn

Saturn is a decentralized content delivery network (CDN) for Filecoin. It aims to bridge the gap between the content being stored on Filecoin and users wishing to quickly retrieve that content.

In this context, we can think of Saturn as content delivery market. On the buyer side, websites pay Saturn to have the content they store on Filecoin delivered to their users quickly and reliably. On the seller side, node operators make their cache and bandwidth available to Saturn and earn Filecoin by fulfilling requests. Saturn thus serve as a centralized market maker, connecting websites that need content delivery to resources that would otherwise not be utilized. 

Previous authors have studied how to price CDNs, both centralized and decentralized.  For instance, Hosanagar et al. [1] did an empirical analysis of how to price the service provided by centralized CDNs. On the other hand, Khan Pathan et al. [2] proposes a system (and the corresponding economic model) to assist CDNs to connect and share resources, while Garmehi et al. [3] describe a scheme that incorporates peer-to-peer resources from the network's edge to a classical CDN. Both rely on a auction model and profit maximization for pricing.

Although related, this work does not translate to the particular use-case of Saturn. To kick off the network, Saturn will start with some funding from PL and pay the early node operators from that pool of initial funding. As such, for the purpose of the first version of Saturn, we are only interested in defining how this initial pool should be split among node operators. In other words, we focus on the seller side of the retrieval market and try to define an optimal distribution of rewards that incents participation towards a set of shared goals.

This is similar to a concept proposed by Wilkins et al. [4], the marketized-commons platform, which is defined as a platform attempting to "incentivize collaborative efforts through market principles". In this model, everyone benefits from the collective action, but participation is costly. In Saturn, all internet users will benefit from a faster content delivery, while node operators will carry the cost of participation.

Interestingly, Wilkins et al. [4] argues that financial incentives are not the main driver of participation in the commons and that platforms that solely rely on financial incentives have a hard time sustaining participation. To combat this, the authors suggest taking into consideration the participants' social identities. Specifically for incentives, they state that the platform's reward system needs to incorporate the social values of the group and reward collective behavior. This is a valuable takeaway for Saturn. In our case, we need to be clear about the collective goals for the network and incent node operators to achieve them as a group.

Another important problem Saturn will need to meet is the issue of honesty. Because we don't have an efficient way to cryptographically proof retrievals, we need to take the logs submitted by node operators as the signal to distribute rewards. As such, the network is open to attack vectors where untrustworthy nodes submit fake or altered logs to collect more rewards.

The issue if dishonesty in online platforms in not new. A common place where this issue arises is in online marketplaces and C2C commerce, where authors usually tackle dishonesty through user feedback and reputation systems [5] [6] [7]. Dewan and Dasgupta [8] and Aljuraidan et al. [9] also explore how reputation systems can aid with dishonesty, although in different applications. Dewan and Dasgupta [8] look into outsourcing computation while Aljuraidan et al. [9] analyze peer-to-peer networks. All the authors conclude that reputation systems (and the potential lost of future rewards) can be an effective way of incenting good behavior. However, they can take advantage of user feedback and/or "verified tests" to feed their reputation systems, which Saturn is not expected to have in a first phase.

In addition to reputation systems, penalties can be used to incent good behavior. Kroupa [10] analyze the impact of punishment in human cooperation and concluded that punishment can be an efficient way of maintaining cooperation. However, punishment requires a system to detect undesired behavior and penalties that are large enough to balance the system's detection rate.


## Reward distribution design

:::info
:hammer: WIP
:::

Before discussing what options there are for distributing rewards among Station Operators, there are some principles we wish to meet:

1. Simplicity over complexity -> we only add complexity if it serves a purpose and, thus, we try to build the simplest process that achieves the goal.
2. Bounded rewards -> since we are still in a testing phase, we should limit the daily rewards to avoid overspending in case of DDoS attacks and other anomalous behavior
3. Incent a reliable and performant service -> these are the two main attributes we care about when designing incentives. First, we want Operators to serve a high volume of retrievals with a high bandwidth / fast upload time. Second, we want Operators to be reliable and fail gracefully.
4. Incent honesty -> Operators should be incentivized to report their own faults
5. Preference towards free market -> we try to leverage free market mechanics and supply-demand to avoid having to set a price for content delivery. Price setting on new services is a hard problem and letting the market decide on the market is a good design when we have price uncertainty.

:::warning
:warning: Open question: do we want to incent actual service or offered service? E.g., do we want to reward the actual bandwidth delivered (which depends on the clients and other external factors) or do we want to reward the bandwidth the Operator is capable of providing?
:::

### Reward pool

Fixed vs. variable

Single vs. multiple

### Penalties

Decrease rewards? How much?


## Simulating Saturn's "economy"

:::info
:hammer: WIP
:::

### Fair distribution of rewards

TBD

### Incentivizing honesty

TBD

## References

[1] Hosanagar, K., R. Krishnan, M. Smith, and J. Chuang. 2004. ‘Optimal Pricing of Content Delivery Network (CDN) Services’. In 37th Annual Hawaii International Conference on System Sciences, 2004. Proceedings of The, 10 pp.-. https://doi.org/10.1109/HICSS.2004.1265480.


[2] Khan Pathan, Al-Mukaddim, Rajkumar Buyya, James Broberg, and Kris Bubendorfer. 2007. ‘Economy-Based Content Replication for Peering Content Delivery Networks’. In Seventh IEEE International Symposium on Cluster Computing and the Grid (CCGrid ’07), 887–92. https://doi.org/10.1109/CCGRID.2007.48.

[3] Garmehi, Mehran, Morteza Analoui, Mukaddim Pathan, and Rajkumar Buyya. 2015. ‘An Economic Mechanism for Request Routing and Resource Allocation in Hybrid CDN–P2P Networks’. International Journal of Network Management 25 (6): 375–93. https://doi.org/10.1002/nem.1891.

[4] Wilkins, Denise, Bashar Nuseibeh, and Mark Levine. 2019. ‘Monetize This? Marketized-Commons Platforms, New Opportunities and Challenges for Collective Action’. In Human-Computer Interaction. Design Practice in Contemporary Societies, edited by Masaaki Kurosu, 130–47. Lecture Notes in Computer Science. Cham: Springer International Publishing.

[5] Lax, Gianluca, and Giuseppe M. L. Sarné. 2008. ‘CellTrust: A Reputation Model for C2C Commerce’. Electronic Commerce Research 8 (4): 193–216. https://doi.org/10.1007/s10660-008-9019-8.

[6] Sharma, Neeraj Kumar, Vibha Gaur, and Punam Bedi. 2014. ‘Improving Trustworthiness in E-Market Using Attack Resilient Reputation Modeling’. International Journal of Intelligent Information Technologies (IJIIT) 10 (3): 57–82. https://doi.org/10.4018/ijiit.2014070104.

[7] Fan, Ming, Yong Tan, and A.B. Whinston. 2005. ‘Evaluation and Design of Online Cooperative Feedback Mechanisms for Reputation Management’. IEEE Transactions on Knowledge and Data Engineering 17 (2): 244–54. https://doi.org/10.1109/TKDE.2005.26.

[8] Dewan, P., and P. Dasgupta. 2005. ‘Securing P2P Networks Using Peer Reputations: Is There a Silver Bullet?’ In Second IEEE Consumer Communications and Networking Conference, 2005. CCNC. 2005, 30–36. https://doi.org/10.1109/CCNC.2005.1405139.

[9] Aljuraidan, Jassim, Lujo Bauer, Michael K. Reiter, and Matthias Beckerle. 2017. ‘Introducing Reputation Systems to the Economics of Outsourcing Computations to Rational Workers’. In Financial Cryptography and Data Security, edited by Jens Grossklags and Bart Preneel, 60–77. Lecture Notes in Computer Science. Berlin, Heidelberg: Springer. https://doi.org/10.1007/978-3-662-54970-4_4.

[10] Kroupa, Sebestian. 2014. ‘Love or Fear: Can Punishment Promote Cooperation?’ Evolutionary Anthropology: Issues, News, and Reviews 23 (6): 229–40. https://doi.org/10.1002/evan.21430.
