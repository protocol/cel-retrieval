---
title: Reward distribution for Saturn
tags: Saturn aliens, Retrievals
description: Analysis of different options for distributing rewards in Saturn
breaks: false
---

[![hackmd-github-sync-badge](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q/badge)](https://hackmd.io/MqxcRhVdSi2txAKW7pCh5Q)

# Reward distribution for Saturn

#### Maria Silva and Amean Asad, September 2022

In this report, we discuss the technical details of Saturn's reward distribution module. This is one of the two main components of [Saturn's Treasury](https://hackmd.io/@cryptoecon/SJIJEUJbs/%2FmGKG1Iz-RRmbMzsAX468iQ).

We start with a summary of similar work and projects. Then, we discuss all the options and technical details of how to design the reward distribution for Saturn. We conclude the report with an empirical analysis of the options and how they may influence honesty and service [This last part is still WIP!!].

## Retrieval markets and Saturn

Saturn is a decentralized content delivery network (CDN) for Filecoin. It aims to bridge the gap between the content being stored on Filecoin and users wishing to quickly retrieve that content.

When a user visits a website using Saturn's CDN, a request for content is submitted Saturn. The network routes the request to an L1 node, who becomes responsible for serving that request. If the L1 node has the content cached, they can simply send the content to the user. If not, they will send a request to a group of L2 nodes close-by. The entire set of L2 nodes connected to a given L1 node are its “swarm” and an L2 node only connects to L1 nodes in its vicinity. If the L2 nodes have the desired content cached, they will send it to the L1 node, which in turn will send it to the original user. If none of the L2 nodes have the content, the L1 node will cache miss to the IPFS gateway or Filecoin's Storage Providers. In the end, the L1 and L2 nodes will send logs of these interactions to Saturn's central orchestrator and will be paid by Saturn accordingly.

<div style="text-align:center">
<img width="550" src="https://github.com/protocol/cel-retrieval/blob/master/saturn-aliens/reports/images/saturn_value_flow.drawio.png?raw=true">
<br>
<br>
</div>

In this context, we can think of Saturn as content delivery market. On the buyer side, websites pay Saturn to have the content they store on Filecoin delivered to their users quickly and reliably. On the seller side, L1 and L2 nodes operators make their cache and bandwidth available to Saturn and earn Filecoin by fulfilling requests. Saturn thus serve as a centralized market maker, connecting websites that need content delivery to resources that would otherwise not be utilized. 

Previous authors have studied how to price CDNs, both centralized and decentralized.  For instance, Hosanagar et al. [1] did an empirical analysis of how to price the service provided by centralized CDNs. On the other hand, Khan Pathan et al. [2] proposes a system (and the corresponding economic model) to assist CDNs to connect and share resources, while Garmehi et al. [3] describe a scheme that incorporates peer-to-peer resources from the network's edge to a classical CDN. Both rely on an auction model and profit maximization for pricing.

Although related, this work does not translate to the particular use-case of Saturn. Saturn's servers are decentralized and, as such, the costs and reward structures are not compatible with a centralized or hybrid model. In addition, for the purpose of the first version of Saturn, we are interested in defining how a given pool of rewards should be split among node operators. In other words, we focus on the seller side of the retrieval market and try to define an optimal distribution of rewards that incents participation towards a set of shared goals.

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

However, a variable pool has the disadvantage of being less predicable, which can deter node operators to make big upfront investments. Another option is to have a **hybrid pool that contains a pre-determined base component and a variable component**. The base component would be funded by a fixed initial pool of Filecoin while the variable component would be funded by the new clients joining the network. This way, the base pool gives more predictability, whiles the variable pool encourages growth and adoption.

Connected to this consideration is the definition of the **payout window for the pool**. For a given new inflow of funding to the reward pool, we need to define how the total funding will be split daily to pay rewards. Blockchains such as Bitcoin use an exponential decay model, where mining rewards get exponentially smaller with time. This model benefits early adopters so that the network achieves a faster growth at the start. Another option is to split the total funding equally throughout the duration of the client agreement, which would be the simplest approach. It is not clear what is the best approach here, so this is **still to be discussed with the team**.

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

Taking into account that this first iteration of the system aims to kick-start the network and learn how people will use (and misuse) Saturn, having low entry barriers seems to be more important. As such, we propose to **not have any collateral in the start** and reevaluate its need for future iterations.

### Service scoring functions

A service scoring function is a function that maps service metrics, such as bandwidth, node type or TTFB, into a real number $s_i$ that defines the ratio of rewards to be given to a specific node operator $i$. 

More concretely, if we have $n$ nodes ($i=1, 2, ..., n$), an amount of rewards to distribute, $R$, and service metrics for node $i$ defined by $m_i \in \mathcal{M}$, a service scoring function is a function $S: \mathcal{M} \to \mathbb{R}$ such that:

1. The reward paid to node $i$ is $r_i = S(m_i) \cdot R$
2. $\sum_{i=1}^n S(m_i) = 1$

Before detailing the scoring functions, we need to define the service metrics. In Saturn, service can be measured by three main metrics:

1. Bandwidth — Number of bytes transferred from Saturn to its end users, in a given time-interval. This is the main metric we want to score as it encodes the network's “usage” and is the main driver of costs for node operators.
2. Time-to-first-byte (TTFB) and total download time — one of the behaviors we wish to see in Saturn is a fast content delivery and, as such, the speed of the content delivery is an important incent vector. One way we can measure it is through the TTFB and total download time recorded by the end-user. Note that since we do not yet collect logs from the end-users, we will need to estimate the average TTFB and the download speed using a sample of requests performed by the orchestrator. In addition, the clients onboarded (aka the content publishers) will be able to collect both metrics, so we can also leverage their logs to estimate the average TTFB and download speed.
3. Uptime — Reliability is another behavior we wish to see in Saturn. L1 nodes are expected to be online and, in case of failure, warn the network and fail gracefully. Another point here is that in rewarding uptime, we are, in a way, rewarding available service also. The previous two metrics focus on the actual service experienced by end-users, while uptime considers the nodes' availability to perform services for the network.

:::warning
:warning: there is another behavior we are not discussing here - geographical coverage. Incentivizing certain regions by providing bigger rewards would be more easily addressed using multiple pools. This will be something to tackle in later versions, once we have a clearer idea of where the users and node operators are located.
:::

#### Bandwidth scoring function

When scoring bandwidth, the higher the bandwidth, the larger the share of rewards should be. Thus, not only the scoring function needs to meet criteria defined above, but it also needs to be strictly monotonically increasing. We can achieve this using a positive power of the bandwidth fraction. More concretely, if we have:

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

It is not clear what the optimal value for $k$ is. Therefore, this will be a parameter we will tune during the simulation analysis.


#### Download times scoring function

For TTFB and download speed, we cannot directly use the functions we used for bandwidth. The reason is two-fold:

1. Having lower download times is a good thing, which means the scoring function needs to be monotonically decreasing.
2. Nodes may contribute both positively and negatively to the network's download times. In other words, if many nodes join the network with a high times, they can lower the entire network performance. On the other hand, for bandwidth, nodes can only add more bandwidth, so they cannot negatively affect the network on that particular metric.

Another important consideration here is that a single request with a very low speed is not very valuable to the network in general. One can only say that Saturn delivers a *fast* service when a significant portion of node operators are *fast*. With this in mind, we are not interested in incentivizing single nodes to decrease their download times indefinitely, but instead we want the entire network to be better than a certain threshold of each download time metric.

One way to encode this incentive is to use the percentage of requests of a given node operator with both TTFB and total download time lower than some predefined thresholds. With this new metric, we can use the exact same functions defined for bandwidth. At the same time, we avoid rewarding node operators on achieving great speeds on a few requests and, instead, reward by how many of their requests are better than the thresholds.

Why do we use the percentage instead of the number of requests? If we chose the number of requests, we would be indirectly considering network usage in this incentive. Two node operators with speeds always bellow the thresholds would receive different rewards solely based on the number of requests they served.


#### Uptime scoring function

We currently have a table called `health_check_failures` that stores data on "downtime" events from nodes. Every minute, the orchestrator sends a health check to every node and stores the results. Nodes that fail the health check are logged to the `health_check_failures` table. 

We can get an estimate of downtime from this information. The proposal is to compute the percentage of health check failures per given amount of time. Let $d_i$ represent the health check failure percentage for node $i$. We define $u_i = 1 - d_i$ as the uptime estimate for node $i$. 

To give an example, let's assume we run our payments every hour. For every hour we have 60 health checks (1 per min). If node $k$ failed 20 health checks, then:

$$
d_k = \frac{20}{60} = \frac{1}{3} \\
\implies u_k = 1 - d_k = \frac{2}{3}
$$

It is important to note that this method gives only an estimate of uptime. It is also aggressive with how it penalizes nodes for downtime because it assumes that if a node fails a health check then it must be down for a whole minute. In addition, it will miss downtime events that happen between health checks.

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

Thinking of L2 swarms as cache-extensions of their L1 nodes is a good analogy to set payouts. In a way, L2s contribute to the performance of L1 nodes. The larger and more performant the swarm, the better L1 nodes will be at delivering content. As such, it makes sense for L1s to share some of the rewards they receive with the swarms. In particular, we can use the previous scoring functions to distribute rewards among L1 nodes. Then, based on how much each L2 contributed to the service the L1s provided, a part of the rewards distributed will be passed on to the swarms.

With this in mind, the question to answer is how can we measure the contribution of L2 nodes to the service provided by the L1 nodes? When a request is submitted to an L1 node, there are two possibilities - either the L1 node has the content cached or it does not. If the content is cached, then the swarm has no contribution to the service. However, if the content is not cached, the L1 node will request the data to its swarm. The L2 nodes that have that content in cache will start sending it to the L1 node and, as such, a part of the rewards obtained from that request should be shared with the L2 operators that sent the content.

Therefore, we can use the share of bandwidth served from L1 nodes using cache to split the rewards between L2 and L1 nodes. If $R$ is the total reward to be distributed in a given epoch and $c$ is the ratio of bandwidth from L1s where the cache was used, then the total reward to be paid to L2 nodes will be $R^* = (1-c) \cdot \gamma \cdot R$, for $\gamma \in [0,1]$. Note that we are not giving 100% of the rewards resulting from cache-miss requests to L2s since even in these requests, L1s have a very important role. As such, L2s only receive a part of those rewards encoded in the parameter $\gamma$.

Once we have $R^*$, we can use the same scoring functions to redistribute $R^*$ among L2 nodes. An important note here is that uptime is not required for L2s and, as such, we can either lower their uptime threshold or remove the scoring function entirely.

:::warning
:warning: Another consideration here is whether we should pay L2s at all. Recall that Wilkins et al. [4] argued that financial incentives are not the main driver of participation in the commons and can sometimes worsen participation. Are there any other types of incentives we could offer instead? E.g., access to premium features or some sort of bragging items?
:::

## Simulating Saturn rewards

### Fair distribution of rewards (L1 nodes)

The main goal of this analysis is to compare how different scoring functions impact the distribution of rewards among L1 node operators in a **single epoch**. Throughout the analysis we assume that we have 1000 L1 operators, and we generate their service metrics using specific statistical distributions. The plots below show the histograms for the three service metrics generated - total bandwidth, ratio of requests simultaneously above the speed thresholds (i.e. TTFB and download time), and uptime percentage.

| ![](https://i.imgur.com/buTtSZ8.png) | ![](https://i.imgur.com/aDP8SXA.png) | ![](https://i.imgur.com/0nHGvle.png) |
| ------------------------------------ | ------------------------------------ | ------------------------------------ |

Using these randomly generated service metrics, we tested different scoring functions, namely:

1. Linear combination:
   1. Balanced linear - individual linear scoring functions (exponent $k=1$) + linear combination split equally between the three services 
   2. Balanced sublinear - individual sublinear scoring functions + linear combination split equally between the three services 
   3. Balanced supra-linear - individual supra-linear scoring functions + linear combination split equally between the three services
   4. High bandwidth linear - individual linear scoring functions + linear combination with higher weight for bandwidth
   5. High bandwidth sublinear - individual sublinear scoring functions + linear combination with higher weight for bandwidth
   6. High bandwidth supra-linear - individual supra-linear scoring functions + linear combination with higher weight for bandwidth
2. Direct multiplication:
   1. All sublinear - sublinear exponent $k=0.5$ for the three metrics
   2. All linear - linear exponent $k=1$ for the three metrics
   3. All supra-linear - supra-linear exponent $k=2$ for the three metrics
   4. Bandwidth smooth - linear exponent for bandwidth ($k = 1$) and sublinear exponent for the remaining two metrics ($k = 0.5$)

For each scoring functions, we computed the reward distribution for each of the 1000 node operators in a single epoch. Note that here we assume that the total reward to be distributed is $R=100$.

The first conclusion here is that the choice of scoring function has a significant impact on the overall distribution of rewards among node operators. The following table illustrated this by reporting the minimum and maximum reward paid to a single operator and the [Gini index](https://en.wikipedia.org/wiki/Gini_coefficient). Recall that the Gini index is a measure of statistical dispersion that represents wealth inequality within a group. It varies between 0 and 1, with 0 expressing perfect equality and 1 expressing maximal inequality.

|                       | Scoring function      | Gini index | Min. payout | Max. payout |
| --------------------- | --------------------- | ---------- | ----------- | ----------- |
| Linear combination    | Balanced sublinear    | 0.079901   | 0.06        | 0.15        |
|                       | Balanced linear       | 0.143888   | 0.05        | 0.22        |
|                       | Balanced supra-linear | 0.369626   | 0.01        | 0.61        |
|                       | High-bw sublinear     | 0.117397   | 0.05        | 0.17        |
|                       | High-bw linear        | 0.210802   | 0.04        | 0.28        |
|                       | High-bw supra-linear  | 0.380111   | 0.01        | 0.57        |
| Direct multiplication | All sublinear         | 0.239131   | 0.01        | 0.24        |
|                       | All linear            | 0.427477   | 0.001       | 0.50        |
|                       | All supra-linear      | 0.684226   | 0.000002    | 1.47        |
|                       | Bandwidth smooth      | 0.419714   | 0.001       | 0.48        |


As expected, the sublinear functions lead to the highest equality in rewards distribution, while the supra-linear function lead to the highest inequality in reward payouts. In other words, with supra-linear functions, we are rewarding more the high-performers at the expense of the low performers.

In addition, the direct multiplication functions tend to lead to a higher concentration of rewards among high performers, when compared with the linear combination function. The only exception is the all sublinear, which has a lower Gini than the two most concentrated function among the linear combination group.

There is another different in the dynamics between the linear combinations and the direct multiplication functions, which is illustrated in the next two plots. Here we see the total payout given to each node operator against the share of bandwidth they provided.

| ![](https://i.imgur.com/1gNfug1.png) | ![](https://i.imgur.com/yOGMLNG.png) |
| ------------------------------------ | ------------------------------------ |

Once again, we confirm the effect of the exponent $k$ on the rewards' distribution - the share of rewards grows faster than the share of bandwidth in supra linear functions, while the reserve happens in the sublinear functions.

However, the interesting observation here is how much the linear functions smooth-out poor performances in the other metrics besides bandwidth. In other words, the drop in rewards a node gets by a bad performance in speed and/or uptime is much lower with the linear functions than the direct multiplication functions. The effect is most accentuated in the all supra-linear scoring function, which a lower performance in either download speed or uptime leading to a significant decrease in rewards. 

This is a very relevant mechanism as we are incenting nodes to be good at all the metrics and, at the same, penalizing heavily any decrease in performance. Note that the bandwidth smooth follows the same trend as the all linear, but since the speed and uptime metrics get a sublinear exponent, the "penalty" for poor performance is smoothed.

:::info
:hammer: Final suggestion!
:::

:::warning
:warning: An important caveat: the reward distribution obtained above depend heavily on the service metrics generated. If we were to observe a higher dispersion in performance, then the reward inequality would increase. In addition, as expected, this increase would be felt more heavily on the supra-linear functions.
:::

### Incentivizing honesty

When setting penalties for dishonesty, there are two main metrics that need to be considered - the true positive rate (i.e., the probability of a cheater being detected) and the false positive rate (i.e. the probability that an honest node is flagged as a cheater). Both of these metrics need to be estimated through known cases detected in the past.

If we have these two metrics, then we can define bounds for the penalty adjustment applied to single nodes using two main assumptions:

1. Lower bound assumption - the penalty should be large enough so that it is not economically advantageous to cheat. In other words, the expected reward of cheating (taking into account the probability of detection) needs to be negative.
2. Upper bound assumption - the penalty should be small enough so that it does not hurt honest nodes considerably. In other words, the expected reward obtained by an honest node should be higher than a certain percentage of the total rewards.

#### Deriving lower bound

Given the following variables:

- $R_t$, the reward a cheating node receives at payout time $t$, before any penalty is applied.
- $\alpha$, the true positive rate of the log detection system (we are assuming this rate is stable through time). It can be interpreted as the probability of a cheating node being flagged.
- $P$, the penalty in case of detection.
- $n$, the number of past payouts at payout time $t$.

Then, the lower bound assumption requires that the expected reward of cheating be negative, which leads to the following inequality:


$$
\begin{align*}
   & \sum_{t=1}^n \bigg( (1-\alpha)\cdot R_t + \alpha (R_t - P) \bigg) < 0  \Longleftrightarrow\\
   & \Longleftrightarrow \sum_{t=1}^n \bigg(R_t - \alpha \cdot P \bigg) < 0  \Longleftrightarrow\\
   & \Longleftrightarrow \sum_{t=1}^n R_t - \alpha \cdot n \cdot P < 0  \Longleftrightarrow\\
   & \Longleftrightarrow P > \frac{1}{\alpha} \cdot \frac{\sum_{t=1}^n R_t}{n}
\end{align*}
$$

In other words, the penalty needs to be larger that $1 / \alpha$ times the average reward of the node (before penalties).

#### Deriving upper bound

Given the following variables:

- $R_t$, the reward an honest node receives at payout time $t$, before any penalty is applied.
- $\beta$, the false positive rate of the log detection system (we are assuming this rate is stable through time). It can be interpreted as the probability of an honest node being flagged.
- $\tau$, the ratio of rewards that honest nodes should receive on average.
- $P$, the penalty in case of detection.
- $n$, the number of past payouts at payout time $t$.

Then, the upper bound assumption requires that the expected reward of honest node be above $\tau$ times the rewards before penalties, which leads to the following inequality:

$$
\begin{align*}
   & \sum_{t=1}^n \bigg( (1-\beta)\cdot R_t + \beta (R_t - P) \bigg) > \tau \sum_{t=1}^n R_t  \Longleftrightarrow\\
   & \Longleftrightarrow \sum_{t=1}^n \bigg(R_t - \beta \cdot P \bigg) > \tau \sum_{t=1}^n R_t  \Longleftrightarrow\\
   & \Longleftrightarrow \sum_{t=1}^n R_t - \beta \cdot n \cdot P > \tau \sum_{t=1}^n R_t  \Longleftrightarrow\\
   & \Longleftrightarrow P < \frac{1-\tau}{\beta} \cdot \frac{\sum_{t=1}^n R_t}{n}\\
\end{align*}
$$

In other words, the penalty needs to be smaller that $(1-\tau) / \beta$ times the average reward of the node (before penalties).

#### Bounds estimation

In this section, we plot the *penalty adjustment* derived above, assuming a range of values for the true positive rate $\alpha$, the false positive rate $\beta$ and the minimum reward ratio $\tau$. Note that the *penalty adjustment* is a fixed number to be multiplied by each node's average reward (excluding penalties).

The next plots show the values obtained:

| ![](https://hackmd.io/_uploads/ByWBrCLWs.png) | ![](https://hackmd.io/_uploads/rk-Pr0UZj.png) |
| --------------------------------------------- | --------------------------------------------- |

As we can see, there is a limited window for the penalty adjustment that meets both bounds. In addition, the worse the detection system (i.e. the lower the true positive rate and the higher the false positive rate), the smaller this window is. In fact, these curves already give us some goals that we should meet with the detection system, namely, having a false positive rate lower than 5% and a true positive rate higher than 25%.

Another consideration is that the penalty needs to be bigger than 1 (i.e. needs to be bigger than the average reward per payout). This is intuitive since, were it not the case, dishonest nodes would always gain some money because no detection system will catch all the fake logs. However, this creates a problem in a situation where collateral is not required - if a node is flagged, and it is assigned a negative reward, where is that money coming from?

A possible solution is to introduce some delay to rewards. When a node submits logs, a reward is computed and stored for some time. If, in the meantime, that nodes gets assigned a penalty, it will be deducted from the stored rewards. Finally, the rewards that "vest" at each day will be sent to the node, minus the penalties applied. Therefore, at each point in time, all nodes have money "at stake" that can be slashed to cover for penalties.

:::info
:hammer: Final suggestion: 5 times the average reward per payout seems a good compromise between a low enough false positive rate (2%) and a reasonable true positive rate (20%).
:::

:::warning
:warning: We still need to check whether the payout frequency impacts the long-term aggregated penalties
:::

### Full simulation (with sample data)

:::info
:hammer: WIP
:::

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
