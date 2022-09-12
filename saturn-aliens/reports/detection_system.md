---
title: Saturn's log detection module
tags: Saturn aliens
description: Design and analysis of Saturn's logs detection module
breaks: false
---

[![hackmd-github-sync-badge](https://hackmd.io/WihFXzN9QteSwIxHW5zKeQ/badge)](https://hackmd.io/WihFXzN9QteSwIxHW5zKeQ)

# Saturn's log detection module

#### Maria Silva, September 2022

In this report, we present an in-depth analysis of Saturn's log detection module. This is component of Saturn responsible for detecting any doctored or fake logs submitted by node operators. Therefore, it serves as a protection layer against cheating and the consequent distribution unwarranted rewards.

## Motivation

As a decentralized content delivery network (CDN), Saturn relies on the participation of willing operator nodes. Anyone with good enough hardware resources is free to join, contribute to Saturn's service and, in return, receive some rewards. Rewards in Saturn depend on three main sources of data:

1. Saturn's orchestrator module: a centralized service that will make test requests to operator nodes in other to measure their performance in terms of download speeds and uptime.
2. Operator nodes: every time an operator node processes a request, they will log the request (along with some related stats) and send it to the orchestrator.
3. Client websites: content publishers using Saturn to accelerate their online distribution will have Saturn code running in their applications, which will log metrics about each user accessing their content. Note that this data will only be available after Saturn onboards clients to network.

:::warning
:warning: Can we think of ways in which node operators can game the data coming from the orchestrator? In other words, can the download speed and uptime performance metrics be gamed?
:::

Since there are no feasible solutions for trustless verification of content delivery, we cannot assume that the data Saturn receives from its operator nodes is correct. These logs can be doctored, either by hacking Saturn's code to directly edit the logs or by using a bot to make "fake" requests. 

If we didn't have a detection system in place (together with penalties in case of detection), there would be a clear incentive for "rogue" nodes to cheat the system and steal rewards from other honest participants.

Thus, Saturn's log detection module aims to solve this problem by finding and flagging doctored or fake logs submitted by node operators. 

## Design overview

When we talk about suspicious behavior, there are two separate levels at which we can detect it:

1. **Request level:** Level where we look at individual logs, which corresponds to detecting specific requests that do not look legitimate. An example here would be a request that has an impossibly fast duration. At this level, we screen all the individual requests coming from the logs service and flag any that looks suspicious. The output is a list of flagged requests and the origin of their flags.
2. **Operator level:** Level where we do not pinpoint a specific log that looks suspicious but, instead, we look at the general behavior of individual node operators. An example here would be an operator that is logging an impossibly high number of requests. At this level, we aggregated the raw logs for each operator and flag any that looks suspicious. The output is a list of flagged nodes and the origin of their flags.

Both levels are important and will give different views on the underlying data. It is not a matter of which level is better. Instead, we will do detection at both levels in parallel. 

Another consideration is the detection techniques we plan to use. Since the initial version of the detection module has to be designed before Saturn has real active users, we start with a simple heuristics-based detection system, tuned with sensible assumptions about how users will operate with Saturn and the testing data we already have. The next section goes in more detail about these heuristics.

After Saturn is launched and more data is collected, we plan to iterate on this simple system by improving the heuristics and experimenting with more sophisticated detection methods such as anomaly detection models, supervised models, and active learning models.

In addition to this behavior-based detection approach, detection can also be done by cross-checking data from the two sides of the market. Once Saturn begins to onboard content publishers to the network (which will be paying for the service), we can use logs submitted by these clients to cross-check the logs provided by node operators. None of the sides have incentives to collude in cheating the network because one of the sides will always pay to the rewards of the other side. However, this approach will not be available in the first version of the system because Saturn does not yet have clients.

:::warning
:warning: Can we think of other ways of doing such cross-checks?
:::

## Heuristics

:::info
:hammer: WIP
:::

Heuristics are defined as simple rules that encode a specific behavior we are trying to avoid. In this module, we will have heuristics for the two levels described before - requests and operators.

The next table describes all the heuristics proposed to be included in the detection system and highlights the reasoning for each heuristic. It is important to note that this is a first proposal, and it is likely to change as the project matures.

|                Name                |  Level   |                                              Description                                              |                                                                                                      Reasoning                                                                                                      |
| :--------------------------------: | :------: | :---------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|         High request count         | Operator |                Flag operators with a total number of requests higher than a threshold                 |                                             Operators may inject fake logs to bump their rewards. This rule catches operators that inject a massive number of requests                                              |
|           High bandwidth           | Operator |                        Flag operators with a bandwidth higher than a threshold                        |                                    Operators may change their logs to bump their rewards. This rule catches operators where these changes add up to an impossibly high bandwidth                                    |
|       Bot client (requests)        | Request  |   Flag the requests coming from a client whose total number of requests is higher than a threshold    |                                Operators may employ bots to bump the number of requests and gain more rewards. This rule catches clients that have too many requests for a real user                                |
|         Bot client (bytes)         | Request  |    Flag the requests coming from a client whose total bytes transferred is higher than a threshold    |                            Operators may employ bots to bump their bytes transferred and gain more rewards. This rule catches clients that are requesting too much data for a real user                             |
| Single client Operators (requests) | Operator |            Flag operators with an average request count per client higher than a threshold            | Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total no. of requests divided by the number of clients will uncover some of these cases. |
|  Single client Operators (bytes)   | Operator |     Flag operators with an average number of bytes transferred per client higher than a threshold     |      Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total bytes divided by the number of clients will uncover some of these cases.      |
|           Self-requests            | Request  |                      Flag requests where the node ID and client ID are the same                       |                                 Operators may try to do requests to themselves to collect more rewards. If they do, we can catch this by comparing the node ID with the client ID.                                  |
|       Doctored content (CID)       | Request  |     Flag requests where the total bytes are higher than the threshold for the CID being requested     |       Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the CID that is being requested        |
|    Doctored content (referrer)     | Request  |   Flag requests where the total bytes are higher than the threshold for the website being requested   |     Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the website that is being requested      |
|           Fast requests            | Request  | Flag requests where the duration is lower than a threshold (split by whether the cache is being used) |        Operators may change the duration of real requests to bump their rewards. This rule catches logs where the request duration is too low for a comparable request (i.e., whether it uses cache or not)         |

Almost all the heuristics proposed have a threshold that needs to be set or tuned. This threshold depends on a single metric that we are comparing against. For instance, in the *fast requests* heuristic, the metric is the request duration. 

We can interpret this problem as a search for univariate anomalies. In the case of the *fast requests* heuristic, we are interested in data points that are too low for the *"normal"* data distribution. Here, the threshold is the point below which we consider a data point *"abnormal"*.

In this document, we do not share the final threshold of each heuristic. If we did, the heuristic would be very easy to cheat! Instead, we discuss the process of getting to the final thresholds. In particular, we use two distinct methods, namely:

1. **Expert judgment:** here we use our knowledge of how Saturn and real requests work to set the threshold. This is mostly used in heuristics where we can easily define what is *impossible*.
2. **Statistical outliers:** here we use data from the test version of Saturn to model the statistical distribution of the underlying metric. Thus, we assume that the data follows a known distribution and that it will be representative of future requests. This test version is running with internal nodes, which means that the observed metrics from real users may be slightly different. However, this is the best approximation we have at the moment. Once we have the distribution for the metric, we set the percentile 99.999 or 0.0001 (1/10000) of the fitted distribution as the threshold candidate.

It is important to note that, in statistical outliers' method, we test all the continuous distributions from [scipy](https://docs.scipy.org/doc/scipy/tutorial/stats/continuous.html#continuous-distributions-in-scipy-stats) and pick the one with the lowest [sum of squared residuals (SSR)](https://en.wikipedia.org/wiki/Residual_sum_of_squares).

Also, in some heuristics, we don't have enough data to fit a distribution (namely the two doctored content heuristics). In these cases, we assume a Gaussian distribution and use the classical threshold for a normal distribution - $\mu + 3 \sigma$.


## Multivariate anomaly detection

:::info
:hammer: WIP - check [PyOD](https://www.andrew.cmu.edu/user/yuezhao2/papers/22-preprint-adbench.pdf) Benchmark
:::

## Future developments

:::info
:hammer: WIP
:::