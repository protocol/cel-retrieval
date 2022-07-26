# Saturn Treasury specification

#### Maria Silva and Ansgar Grunseid, July 2022

###### tags: `Saturn aliens`

***

**Table of contents**

[TOC]

***

## Overview

The Treasury is Saturn's service responsible for processing the transfer logs submitted by node operators (and, in the future, clients) and distributing the rewards accordingly. 

When a client requests a piece of content from Saturn's network, Saturn does not collect data from the client. Instead, Saturn takes the log of the retrieval directly from the Station Operator that served the request.

Since Station Operators are paid for the retrievals they provide, there is a clear attack vector where station operators may change these logs to exploit the network and collect a bigger share of the rewards being distributed.

As such, the Treasury needs to make sure that Station Operators receive the right incentives and that we are capable of detecting fraudulent logs and penalizing the misbehaved operators.

The diagram below illustrates the structure of the Treasure service:


<div style="text-align:center">
<img width="400" src="https://i.imgur.com/WJehybq.png">
<br>
<br>
</div>


The Treasury receives data from the [logs service](https://www.notion.so/pl-strflt/Logs-service-d52cb0fd0bff4c3392fc765720d10b81) and begins by processing it in the fraud detection module. The fraud detection module is responsible for flagging the logs and operators that look suspicious and sending these flagged entities to the reward distribution module.

The approach for the fraud detection module will be to start with simple detection techniques (e.g. heuristics and simple anomaly detection). Then, as we collect more data from Saturn and gain experience from real users, we will iterate and improve the detection model.

Then, the metric aggregator combines the flags produced by the detection module with the raw logs and computes the metrics used to feed the reward calculator. The main output of this module is a table of metrics for each Station Operator, such as the total number of requests, total bandwidth, average request duration, station penalties for bad behavior, and so on.

Next, the reward calculator is the part responsible for processing transfer logs and computing how much FIL each Station Operator will receive. This is the part of the Treasury that will define the main incentives for Station Operators and guarantee that operators are aligned with the long-term vision and goals for Saturn.

Finally, underlying all the components, we have the monitoring module. Because Saturn will function in an agile/iterative setting, we need to be able to monitor the entire payment process to improve both the fraud detection module and the reward calculator. We need to store the the flagged entities and the payouts to Station Operators.

In the next sections, we will describe in more detail the behaviors we want to incentivize/penalize and how each module contributes to this goal.


## Behaviors and incentives

### Good behaviors

At a high level, we wish to incentivize the following behaviors:

* Performance
* Reliability
* Geographical coverage, i.e., we want retrievals to be available across to globe.
* Adherence to Saturn's design. Examples include L1s cache missing to L2s and L2s cache missing to SP's.

At the moment, measuring adherence to Saturn's design will be tricky and, as such, it is out of scope for the Treasury release in September. We are noting it here for future iterations.

These are the behavior we will use to design the formula for distributing rewards among Saturn nodes. Next, we discuss in more detail what each of the remaining 3 behaviors entail and what metrics could be used to measure them.


**Performance**

The most important behavior we want to incentivize is performance. By this we mean the nodes should fulfill requests in such a way that leads to a good experience for clients. With this in mind, the two most important metrics are:

* Time to first byte (TTFB) - how quickly the first requested byte arrives at the client. TTFB measures how quickly the node responded to the request
* Download speed - how quickly the client downloads all the requested. Download speed measures how long it took for node to fulfill the request and, thus, how long the user had to wait to receive the full content. The metric can be taken from the transfer logs using the column `request_duration_sec`.

Note that download speed is often limited on the client's end. In other words, a node may often be able to upload content to a client at 100Mbps, but the node may be on a cellular connection and is only able to download content at 20Mbps. 

There are other metrics we could use to measure performance such as cache hit ratio. However, here we are focussing on what *actually* matters to end users, which is TTFB. In the cache hit ratio example, the higher the cache hit ratio, the lower the TTFB will be, which is the metric already being rewarded.

:::warning
:warning: Need to check with Saturn team how to extract TTFB
:::


**Reliability**

Nodes leaving the network degrade the network performance and experience for users. For example, when a node goes down, it can take up to 60 seconds for that node to be detected as down and removed from the network. Saturn's service worker can recover gracefully, albeit with
degraded performance. Dumb clients without ARC's service worker can't, and their requests may fail.

As such, we want to introduce a mechanism for nodes to gracefully tell the network they will be going offline. If a node goes offline not gracefully, we need to penalize the node. If it goes offline gracefully, we still want to penalize it, although less than going ungracefully.

We can currently extract the uptime data of each station from the orchestrator. This is trusted data since the service is operated centrally and the data is not reported by nodes.

:::warning
:warning: Need to check with Saturn team how to extract these faults from the orchestrator
:::

**Geographical coverage**

Geographical coverage involves having a global network of nodes that can serve requests across different regions. If all the nodes are located in the US, for instance, clients using the Saturn in India will experience some lag.

Therefore, we want to incentivize miners that serve regions with a low coverage and, as such, improve the bandwidth for those clients.

:::warning
:warning: Do we want to limit this incentive to regions that already have clients? And how do we extract this data?
:::


### Bad behaviors

On the other hand, the behaviors we want to avoid mostly revolve around abuse and fraud. Examples include:

* Doctored logs - creating logs of retrievals that didn't happen or changing real logs to improve some variables such as the bytes sent and the request duration. Some examples of metrics nodes can lie about:
  * How long requests took to finish
  * Their TTFB metric
  * Uptime and status. For instance, nodes responding to health checks from the orchestrator while in actuality being offline or in a state of degraded performance to real users.
  * The number of requests they served
  * Amount of bytes they served to clients
* Fake retrievals - retrievals made by operators or other actors that do not correspond to real and lawful clients of the network.
* Retrievals returning the wrong content

In opposition to good behaviors, bad behaviors will be used to penalize nodes. The fraud detection module will be responsible for detecting the behaviors. After a specific log or node is flagged, there are different ways that we can penalize bad-behaving nodes:

* Remove fraudulent logs, reducing the reward to the corresponding node
* Apply a penalty to the total reward the node
* Reduce the node's future rewards by limiting the requests it is able to serve

:::info
:hammer: The final way to penalize these behaviors is still WIP
:::


## Fraud detection module

The fraud detection module aims to detect any doctored or fake logs submitted by station operators. Since the initial version of the Treasury service has to be designed before Saturn has real active users, we start with a simple heuristics-based detection system, tuned with sensible assumptions about how users will operate with Saturn and the testing data we already have.

After Saturn is launched and more data is collected, we plan to iterate on this simple system by improving the heuristics and experimenting with more sophisticated detection methods such as anomaly detection models, supervised models, and active learning models.

Independently of the detection method, when we talk about fraudulent behavior, there are two separate levels at which we can detect it:

1. **Request level:** Level where we look at individual logs, which corresponds to detecting specific requests that do not look legitimate. An example here would be a request that has an impossibly fast duration. At this level, we screen all the individual requests coming from the logs service and flag any that look suspicious. The output is a list of flagged requests and the origin of their flags.
2. **Station level:** Level where we do not pinpoint a specific log that looks fraudulent but, instead, we look at the general behavior of individual Station Operators. An example here would be a Station operator that is logging an impossibly high number of requests. At this level, we aggregated the raw logs for each Station Operator and flag any Operator that looks suspicious. The output is a list of flagged Station Operators and the origin of their flags.


### Heuristics

Heuristics are defined as simple rules that encode a specific behavior we are trying to avoid. In this module, we will have heuristics for the two levels described before - requests and Station Operators.

The next table describes all the heuristics proposed to be included in the detection system and highlights the reasoning for each heuristic. It is important to note that this is a first proposal, and it is likely to change as the project matures.

|               Name                |  Level  |                                              Description                                              |                                                                                                      Reasoning                                                                                                      |
| :-------------------------------: | :-----: | :---------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|        High request count         | Station |                Flag operators with a total number of requests higher than a threshold                 |                                             Operators may inject fake logs to bump their rewards. This rule catches operators that inject a massive number of requests                                              |
|          High bandwidth           | Station |                        Flag operators with a bandwidth higher than a threshold                        |                                    Operators may change their logs to bump their rewards. This rule catches operators where these changes add up to an impossibly high bandwidth                                    |
|       Bot client (requests)       | Request |   Flag the requests coming from a client whose total number of requests is higher than a threshold    |                                Operators may employ bots to bump the number of requests and gain more rewards. this rule catches clients that have too many requests for a real user                                |
|        Bot client (bytes)         | Request |    Flag the requests coming from a client whose total bytes transferred is higher than a threshold    |                            Operators may employ bots to bump their bytes transferred and gain more rewards. This rule catches clients that are requesting too much data for a real user                             |
| Single client Stations (requests) | Station |            Flag operators with an average request count per client higher than a threshold            | Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total no. of requests divided by the number of clients will uncover some of these cases. |
|  Single client Stations (bytes)   | Station |     Flag operators with an average number of bytes transferred per client higher than a threshold     |      Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total bytes divided by the number of clients will uncover some of these cases.      |
|           Self-requests           | Request |                      Flag requests where the node ID and client ID are the same                       |                                 Operators may try to do requests to themselves to collect more rewards. If they do, we can catch this by comparing the node ID with the client ID.                                  |
|      Doctored content (CID)       | Request |     Flag requests where the total bytes are higher than the threshold for the CID being requested     |       Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the CID that is being requested        |
|    Doctored content (referrer)    | Request |   Flag requests where the total bytes are higher than the threshold for the website being requested   |     Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the website that is being requested      |
|           Fast requests           | Request | Flag requests where the duration is lower than a threshold (split by whether the cache is being used) |        Operators may change the duration of real requests to bump their rewards. This rule catches logs where the request duration is too low for a comparable request (i.e., whether it uses cache or not)         |

Almost all the heuristics proposed have a threshold that needs to be set or tuned. This threshold depends on a single metric that we are comparing against. For instance, in the *fast requests* heuristic, the metric is the request duration. 

We can interpret this problem as a search for univariate anomalies or outliers. In the case of the *fast requests* heuristic, we are interested in data points that are too low for the *"normal"* data distribution. Here, the threshold is the point below which we consider a data point *"abnormal"*.

There are two ways one can go about setting these thresholds:

1. **Expert judgment:** here we use our knowledge of how Saturn and real requests work to set the threshold. This may be useful for cases where we can easily define what is *impossible*.
2. **Statistical outliers:** here we use real data from Saturn to model the statistical distribution of the underlying metric. This assumes that the data we have is "normal" and will be representative of future requests. Once we have the empirical distribution for the metric, we can set the threshold such that, with a certain statistical significance, all points falling outside are sampled from a different distribution.

Most likely, we will need to use a mixture of the two strategies, where we start with the statistical distribution and then use expert judgment for further tuning.

:::info
:hammer: More details about the process and the final thresholds will be shared in a dedicated report -> Still **WIP**
:::

### Anomaly detection and ML 

:::info
:hammer: This section will be developed after the first draft is completed.
:::

## Reward calculator 

The reward calculator is the module responsible to computing the payouts to Saturn Operators. Before detailing any formulas, there are some principles we used to design the module:

1. Simplicity over complexity -> we only add complexity if it serves a purpose and, thus, we try to build the simplest process that achieves the goal.
2. Bounded rewards -> since we are still in a testing phase, we should limit the daily rewards to avoid overspending in case of DDoS attacks and other anomalous behavior
3. Incent honesty -> Operators should be incentivized to report their own faults
4. Preference towards free market -> we try to leverage free market mechanics and supply-demand to avoid having to set a price for content delivery. Price setting on new services is a hard problem and letting the market decide on the market is a good design when we have price uncertainty.

:::warning
:warning: Open question: do we want to incent actual service or offered service? E.g., do we want to reward the actual bandwidth delivered (which depends on the clients and other external factors) or do we want to reward the bandwidth the Operator is capable of providing?
:::

:::info
:hammer: This is a very rough draft, and it is still WIP. 
:::


:::info
:thought_balloon: Ansgar made the following proposal:

Apply multipliers to a base function. Multipliers are defined based on some targets we wish nodes to achieve:
  - Base reward is a function of FIL to bytes served
  - Multiplier based on time-to-first-byte (TTFB)
  - Multiplier based on total upload time

Example:

If we're aiming for 500 ms TTFB and 100 Mbps uploads, and an Operator serves a 1 GB response with 400 ms TTFB and 200 Mbps average upload, their reward would be:
  - Base reward: 1 GB = 0.01 FIL
  - TTFB scalar: $(1 + \frac{500 - 400}{500})^2 = 1.21$
  - Upload scalar: $(1 + \frac{200 - 100}{100})^2 = 2.25$
  - Final reward: $0.01 \cdot  1.21 \cdot 2.25 = 0.027225$

Some notes:

- Having goals for the network and rewarding based on how far Operators are from the goals seems to be a good design
- However, we are not letting the market set the price, and we do not have a bound on payouts
- In this design, behaviors are multiplicative -> this means that we are incentivizing Operators to be average on all behavior instead of excellent at one and bad at the others. Is this intended?
- We do not have info on TTFB from the transfer logs. In addition, we have the download time instead of the upload time.
:::

## Annex

![](https://i.imgur.com/iThGfgp.png)
<div style="text-align:center">
<em>Saturn M1 architecture</em>
</div>


