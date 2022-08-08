---
title: Reward distribution for Saturn
tags: Saturn aliens
description: Analysis of different options for distributing rewards in Saturn
breaks: false
---

[![hackmd-github-sync-badge](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q/badge)](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q)

# Reward distribution for Saturn

#### Maria Silva, August 2022

In this report, we discuss the technical details of Saturn's reward distribution module. This is one of the two main components of [Saturn's Treasury](https://hackmd.io/@msilvaPL/r1YWCz4j9).

We start with a summary of similar work and projects. Then, we discuss all the options and technical details of how to design the reward distribution for Saturn. We conclude the report with an empirical analysis of the options and how they may influence honesty and service [This last part is still WIP!!].

## Retrieval markets and Saturn

Saturn is a decentralized content delivery network (CDN) for Filecoin. It aims to bridge the gap between the content being stored on Filecoin and users wishing to quickly retrieve that content.

When a user visits a website using Saturn's CDN, a request for content is submitted Saturn. The network routes the request to an L1 node, who becomes responsible for serving that request. If the L1 node has the content cached, they can simply send the content to the user. If not, they will send a request to a group of L2 nodes close-by. The entire set of L2 nodes connected to a given L1 node are its “swarm” and an L2 node only connects to L1 nodes in its vicinity. If the L2 nodes have the desired content cached, they will send it to the L1 node, which in turn will send it to the original user. If none of the L2 nodes have the content, the L1 node will cache miss to the IPFS gateway. In the end, the L1 and L2 nodes will send logs of these interactions to Saturn's central orchestrator and will be paid by Saturn accordingly.

<div style="text-align:center">
<img width="550" src="https://i.imgur.com/N1kbKa5.png">
<br>
<br>
</div>

In this context, we can think of Saturn as content delivery market. On the buyer side, websites pay Saturn to have the content they store on Filecoin delivered to their users quickly and reliably. On the seller side, L1 and L2 nodes operators make their cache and bandwidth available to Saturn and earn Filecoin by fulfilling requests. Saturn thus serve as a centralized market maker, connecting websites that need content delivery to resources that would otherwise not be utilized. 

Previous authors have studied how to price CDNs, both centralized and decentralized.  For instance, Hosanagar et al. [1] did an empirical analysis of how to price the service provided by centralized CDNs. On the other hand, Khan Pathan et al. [2] proposes a system (and the corresponding economic model) to assist CDNs to connect and share resources, while Garmehi et al. [3] describe a scheme that incorporates peer-to-peer resources from the network's edge to a classical CDN. Both rely on an auction model and profit maximization for pricing.

Although related, this work does not translate to the particular use-case of Saturn. Saturn's servers are decentralized and, as such, the costs and reward structures are not compatible with a decentralized or hybrid model. In addition, for the purpose of the first version of Saturn, we are interested in defining how a given pool of rewards should be split among node operators. In other words, we focus on the seller side of the retrieval market and try to define an optimal distribution of rewards that incents participation towards a set of shared goals.

This is similar to a concept proposed by Wilkins et al. [4], the marketized-commons platform, which is defined as a platform attempting to “incentivize collaborative efforts through market principles“. In this model, everyone benefits from the collective action, but participation is costly. In Saturn, all internet users will benefit from a faster content delivery, while node operators will carry the cost of participation.

Interestingly, Wilkins et al. [4] argues that financial incentives are not the main driver of participation in the commons and that platforms that solely rely on financial incentives have a hard time sustaining participation. To combat this, the authors suggest taking into consideration the participants' social identities. Specifically for incentives, they state that the platform's reward system needs to incorporate the social values of the group and reward collective behavior. This is a valuable takeaway for Saturn. In our case, we need to be clear about the collective goals for the network and incent node operators to achieve them as a group.

Another important problem Saturn will need to meet is the issue of honesty. Because we don't have an efficient way to cryptographically proof retrievals, we need to take the logs submitted by node operators as the signal to distribute rewards. As such, the network is open to attack vectors where untrustworthy nodes submit fake or altered logs to collect more rewards.

The issue if dishonesty in online platforms in not new. A common place where this issue arises is in online marketplaces and C2C commerce, where authors usually tackle dishonesty through user feedback and reputation systems [5] [6] [7]. Dewan and Dasgupta [8] and Aljuraidan et al. [9] also explore how reputation systems can aid with dishonesty, although in different applications. Dewan and Dasgupta [8] look into outsourcing computation while Aljuraidan et al. [9] analyze peer-to-peer networks. All the authors conclude that reputation systems (and the potential lost of future rewards) can be an effective way of incenting good behavior. However, they can take advantage of user feedback and/or “verified tests” to feed their reputation systems, which Saturn is not expected to have in a first phase.

In addition to reputation systems, penalties can be used to incent good behavior. Kroupa [10] analyze the impact of punishment in human cooperation and concluded that punishment can be an efficient way of maintaining cooperation. However, punishment requires a system to detect undesired behavior and penalties that are large enough to balance the system's detection rate.


## Reward distribution design

Before discussing what options there are for distributing rewards among node operators, there are some principles we strive to meet:

1. Simplicity over complexity → we only add complexity if it serves a purpose and, thus, we try to build the simplest process that achieves the goal.
2. Bounded rewards → since we are still in a testing phase, we should limit the daily rewards to avoid overspending in case of DDoS attacks and other anomalous behavior.
3. Incent a reliable and performant service → these are the two main attributes we care about when designing incentives. First, we want operators to serve a high volume of retrievals with a fast download time. Retrieval volume is measured by the total TB's served per day while the download time is measure as the time-to-first-byte (TTFB). Second, we want operators to be reliable and fail gracefully (this is more important for L1s than L2s).
4. Incent honesty → Operators should be incentivized to report their own faults and be truthful about their own logs
5. Preference towards free market → we try to leverage free market mechanics and supply-demand to avoid having to set a price for content delivery. Because we don't know the real costs Saturn nodes will incur when running Saturn, we need to allow for some price discovery. Price setting on new services is a hard problem and letting the market decide on the market is a good design for when we have price uncertainty. 

:::warning
:warning: A note on a free market preference: it is very likely that clients will want to have a stable pricing structure that is simple to understand. So, we will use free market mechanics for price discovery, but we will very likely need a fixed price structure for clients.
:::

Having this in mind, in the next subsections we will detail the various options and mechanisms we can use in Saturn to distribute rewards.

### Reward pool

The reward pool is a set of Filecoin set aside to pay node operators. The idea is that, at each day, we will a use a part of this pool of rewards and distribute it among the resources committed to the network during that day. 

Having a reward pool allows us to achieve two things:
1. We are guaranteed to have bounded rewards have bounded rewards since we cannot spend more that what is already in the pool.
2. We allow for price discovery on the sellers' side. In particular, we are giving a certain budget each day, and we are asking node operators to decide how many resources they are willing to contribute for that budget. When the network reaches an equilibrium, we will be able to compute at what price node operators value their resources and how much we need to charge future clients.

The first consideration when defining the reward pool is whether it should be pre-defined or variable. In a pre-defined pool, the entire amount of rewards to be paid for a given time interval is defined at the start and won't change, independently of the status of the network. A common example is Bitcoin's minting model, where the total amount of rewards to be paid are defined in the protocol and are fully predictable.

On the other hand, in a pool that is not pre-defined (i.e. variable), the total amount of rewards to be distributed may change due to network growth or/and client onboarding. An example for Saturn would be a scenario where content publishers are being onboarded and paying upfront to use the service. In this case, they would be funding a growing reward pool, with new clients onboarded leading to an increase in the total reward pool. The variable pool seems to fit well Saturn for two main reasons:

1. Since Saturn is expected to be a content delivery market, having clients fund the network is the most straightforward way of building a sustainable flow of rewards.
2. Since rewards will depend on the funding being brought into the network, all participants are incentivized to “sell” Saturn and contribute to its usage.

However, a variable pool has the disadvantage of being less predicable, which can deter node operators to make big upfront investments. Another option is to have a hybrid pool that contains a pre-determined base component and a variable component. The base component would be funded by a fixed initial pool of Filecoin while the variable component would be funded by the new clients joining the network. This way, the base pool gives more predictability, whiles the variable pool encourages growth and adoption.

:::warning
:interrobang: In a hybrid reward pool, how do we fund the initial pre-determined pool?
:::

Connected to this consideration is the definition of the payout window for the pool. For a given new inflow of funding to the reward pool, we need to define how the total funding will be split daily to pay rewards. Blockchains such as Bitcoin use an exponential decay model, where mining rewards get exponentially smaller with time. This model benefits early adopters so that the network achieves a faster growth at the start. Another option is to split the total funding equally throughout the duration of the client agreement, which would be the simplest approach. It is not clear what is the best approach here, so **this will be one of the features to test in the simulation**.

The third consideration is whether we should have a singe pool or whether it should be split. Splitting means that we would assign specific amounts of Filecoin to specific groups of nodes (L1 vs. L2s) or to specific incentives (e.g., speed and reliability).

Having multiple pools allows us to tweak the incentives without having to change the reward distribution formulas. For instance, if we wish to incent the network to decrease the average TTFB, we could increase the pool assigned to fast retrievals and, as a consequence, there would be more rewards distributed for that specific behavior. Multiple pools also allow clients to pay differently based on the type of service they wish to have. For instance, a client could put more money into the “speed” pool to incent a faster delivery.

Another area where multiple pools can help is in region-based pricing. If we find that costs across regions are very different, and we wish to incent specific regions to growth, having reward pools per region is a clean way of achieving this.

Having in the mind the principle of simplicity over complexity, **having a single pool seems to be the best approach to start**. This does not mean that the idea cannot be revisited in later versions. However, for the first version, the potential gains do not compensate for the added complexity.


### Penalties

As discussed in the first section, punishment can be a strong driver to incent honesty. However, in order for the incentive to be effective, penalties need to be large enough to make the risk of detection unprofitable. In other words, the expected reward of submitting fake/altered logs should be lower than the expected reward of being honest, taking into account the probability of detection. This is one of the metrics we will model when testing different reward mechanisms in the simulation (more details in the next section).

Independently of the penalty amounts and tuning required, we can think of four main penalty mechanisms, each with an increasing scope of punishment:

1. *Remove flagged logs from the reward calculation*. In this mechanism, we are simply ignoring flagged logs and, thus, node operators have their rewards slightly reduced because we are ignoring the fake logs. 
2. *Give a penalty to the total reward of flagged nodes*. Here a general penalty is applied to the total reward expected to be paid to node operators. This is an individual incentive and directly targets the expected reward of nodes. In addition, this setting allows us to penalize behaviors that can only be detected at the node level (e.g., an impossibly high number of requests served).
3. *Give a penalty to L1 nodes based on how many flagged entities exist in their swarm*. This mechanism aims to discourage collusion between L1 nodes and their swarm. By penalizing L1 nodes based on how their swarm behaves, we incent L1 nodes to report trustfully about how their swarm is performing.
4. *Give a penalty to the entire network based how much flagged activity the network has*. This is the mechanism with the wider scope by making honesty a collective goal for the network. As such, it should deter collusion between nodes and create accountability to the network for “cheating”. It will also deter nodes from attacking other nodes they see as competitors in order to get a bigger pie of the rewards.

Note that these mechanisms are not exclusive, and we can use different mechanisms at the same time. For instance, we can remove flagged logs and give an additional penalty to the total reward of the operator after removing the fake logs. 

The **penalty scope and the exact amount of each penalty will be an important component to test in the simulations**.

Another important consideration around penalties is whether they should only reduce future earnings or whether we should require collateral from nodes and apply penalties on the collateral as well. Having collateral has the advantage of requiring a higher commitment from node operators, while, at the same time, leveraging their loss aversion. On the other hand, collateral will have the disadvantage of increasing the entry barriers for node operators.

:::warning
:interrobang: Do we want to introduce the concept of collateral and staking? Would it make sense to have this only for L1s?
:::

### Service scoring functions

A service scoring function is a function that maps service metrics, such as bandwidth, node type or TTFB, into a real number $s_i$ that defines the ratio of rewards to be given to a specific node operator $i$. 

More concretely, if we have $n$ nodes ($i=1, 2, ..., n$), an amount of rewards to distribute, $R$, and service metrics for node $i$ defined by $m_i \in \mathcal{M}$, a service scoring function is a function $S: \mathcal{M} \to \mathbb{R}$ such that:

1. The reward paid to node $i$ is $r_i = S(m_i) \cdot R$
2. $\sum_{i=1}^n S(m_i) = 1$

Before detailing the scoring functions, we need to define the service metrics. In Saturn, service can be measured by three main metrics:

1. Bandwidth — Number of bytes transferred from Saturn to its end users, in a given time-interval. This is the main metric we want to score as it encodes the network's “usage” and is the main driver of costs for node operators.
2. Time-to-first-byte (TTFB) — one of the behaviors we wish to see in Saturn is a fast content delivery and, as such, the speed of the content delivery is an important incent vector. One way we can measure it is the TTFB recorded by the end-user, which the time between the request being sent and the first byte arriving. Note that since we do not yet collect logs from the end-users, we will need to estimate the average TTFB using a sample of requests performed by the orchestrator. In addition, the clients onboarded (aka the content publishers) will be able to collect TTFB, so we can also leverage their logs to estimate the average TTFB.
3. Uptime — Reliability is another behavior we wish to see in Saturn. L1 nodes are expected to be online and, in case of failure, warn the network and fail gracefully. Another point here is that in rewarding uptime, we are, in a way, rewarding available service also. The previous two metrics focus on the actual service experienced by end-users, while uptime considers the nodes' availability to perform services for the network.

:::warning
:warning: there is another behavior we are not discussing here - geographical coverage. Incentivizing certain regions by providing bigger rewards would be more easily addressed using multiple pools. Could this be something to tackle in later versions, once we have a clearer idea of where the users and node operators are located?
:::

#### Bandwidth scoring function

When scoring bandwidth, the higher the bandwidth, the larger the share of rewards should be. Thus, not only the scoring function needs to meet criteria define above, but it also needs to be monotonically increasing. We can achieve this using a polynomial of the bandwidth fraction. More concretely, if we have:

- $n$ node operators ($i=1, 2, ..., n$)
- $b_i$: total bandwidth served by node operator $i$ in the current epoch

The rewards paid to node operator $i$ in the current epoch are defined by the following **scoring function**:

$S(b_i) := \frac{b_i^k}{\sum_{j=1}^n b_j^k}$

Where $k \in \mathbb{R}^+$ is any real positive value. Although simple, this formula allows for some flexibility rewarding the reward distribution, by varying $k$. The next figure plots the ratio of rewards given to a single node operator in relation to the ratio of bandwidth they contributed. Each line represents a different $k$.

<div style="text-align:center">
<img width="500" src="https://i.imgur.com/x33K5sG.png">
<br>
<br>
</div>

With a supra linear scoring function ($k > 1$), rewards increase faster than the share of bandwidth contributed. This incents operators to rump up their service since they get increasingly more rewards by increasing the bandwidth they service. On the other hand, with a sublinear function ($k<1$), the share of rewards increases slower than the share of bandwidth provided. This incents a higher distribution of rewards since it gets ever harder to get a bigger share of rewards by serving more bandwidth.

It is not clear what the best value for $k$ is. Therefore, this will be a parameter we will tune during the simulation analysis.


#### TTFB scoring function

For TTFB, we cannot directly use the functions we used for bandwidth. The reason is two-fold:

1. Having a lower TTFB is a good thing, which means the scoring function needs to be monotonically decreasing on the TTFB
2. Nodes may contribute both positively and negatively to the network's TTFB. In other words, if many nodes join the network with a high TTFB, they can lower the entire network performance. On the other hand, for bandwidth, nodes can only add more bandwidth, so they cannot negatively affect the network on that particular metric.

Another important consideration here is that a single request with a very low TTFB is not very valuable to the network in general. One can only say that Saturn delivers a *fast* service when a significant portion of node operators are *fast*. With this in mind, we are not interested in incentivizing single nodes to decrease their TTFB indefinitely, but instead we want the entire network to be better than a certain threshold of TTFB.

One way to encode this incentive is to use the percentage of requests of a given node operator with a TTFB lower than a predefined threshold. With this new metric, we can use the exact same functions defined for bandwidth. At the same time, we avoid rewarding node operators on achieving a great TTFB on a few requests and, instead, reward by how much they can be better than the threshold.

Why do we use the percentage instead of the number of requests? If we chose the number of requests, we would be indirectly considering network usage in this incentive. Two node operators with a TTFB always bellow the threshold would receive different rewards solely based on the number of requests they served.


#### Uptime scoring function

:::info
:hammer: Need to check with Saturn team what exact data we can use to measure this!!
:::

#### Combining scoring functions

Now that we have described what functions could be used to score each service, we need to define how we can combine services into a single scoring function.

Let's assume that we have two service metrics we wish to combine and that their individual scoring functions are $S_1(a_i) = \frac{a_i^m}{\sum_{j=1}^n a_j^m}$ and $S_2(b_i) = \frac{b_i^n}{\sum_{j=1}^n b_j^n}$, respectively. In this case, we can define the following two ways of combining the two individual scoring functions into a new scoring functions:

- Linear combination: $S(a_i, b_i) = q \cdot S_1(a_i) + (1-q) \cdot S_2(b_i)$, where $q \in [0,1]$
- Direct multiplication: $S(a_i, b_i)= \frac{a_i^m \cdot b_i^n}{\sum_{j=1}^n a_j^m \cdot b_j^n}$

The linear combination has the advantage of being easy to attribute relative value to each service metric (by changing the $q$ parameter). It is akin to having two reward pools since the service metric $a$ receives the fixed amount of rewards $qR$ while service metric $b$ receives the remaining. It is also simple to interpret, which is a huge advantage.

On the other hand, the direct multiplication incents a more balanced performance among all the services. Because scores are multiplied, if one of the scores is very small, it will have a bigger impact on the total reward than what the linear combination would experience.

It is not clear the best approach here and this is yet another feature we will test with the simulation. However, unless there is a strong argument in favor of the direct multiplication approach, the **interpretability and flexibility of the linear combination approach make it the better option**.

### L2s payouts

In the first section, we described how L1 and L2 nodes are expected to interact within Saturn. Running a L1 node is a more demanding operation than running a L2 node, both in terms of hardware requirements and service expectation. They are the ones serving requests directly to end-users and processing all the requests coming to Saturn. On the other hand, L2 nodes form swarms around single L1 nodes and serve as an extension of their cache. They are home machines, with low hardware requirements, that can go offline as they please.

Thinking of L2 swarms as cache-extensions of their L1 nodes is a good analogy to set payouts. In a way, L2s contribute to the performance of L1 nodes. The larger the swarm, the faster the L1 node will deliver requests. As such, it makes sense for L1s to share the rewards they receive with their swarm. In particular, we can use the previous scoring functions to distribute rewards among L1 nodes. Then, based on how each L2 contributed to the service the L1s provided, a part of the rewards distributed will be passed on to the swarms.

With this in mind, the question to answer is how can we measure the contribution of L2 nodes to the service provided by their L1 node? When a request is submitted to an L1 node, there are two possibilities - either the L1 node has the content cached or it does not. If the content is cached, then the swarm has no contribution to the service. However, if the content is not cached, the L1 node will request the data to its swarm. The L2 nodes that have that content in cache will start sending it to the L1 node and, as such, a part of the rewards obtained from that request should be shared with the L2 operators that sent the content. The exact breakdown of how many rewards should be shared is still to be defined, but the service scoring function here should be simple (maybe consider only bandwidth?). 

:::warning
:interrobang: Can we think of any problems derived from rewarding L2s solely based on bandwidth?
:::

:::warning
:interrobang: What happens if the L1 node needs to cache-miss to the IPFS gateway? If we use the bandwidth provided by L2s, in this case, the L1 node would not share any rewards with its swarm. However, in that case, are we not incentivizing L1s to cache-miss directly to the IPFS gateway?
:::

:::warning
:warning: Another consideration here is whether we should pay L2s at all. Recall that Wilkins et al. [4] argued that financial incentives are not the main driver of participation in the commons and can sometimes worsen participation. Are there any other types of incentives we could offer instead? E.g., access to premium features or some sort of bragging items?
:::

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
