---
title: Saturn Treasury specification V1
tags: Saturn aliens, Retrievals
description: Specification for the first version of Saturn's Treasury system
breaks: false
---

[![hackmd-github-sync-badge](https://hackmd.io/mGKG1Iz-RRmbMzsAX468iQ/badge)](https://hackmd.io/mGKG1Iz-RRmbMzsAX468iQ)

# Saturn Treasury specification

#### Maria Silva and Ansgar Grunseid, September 2022

## Overview

The Treasury is Saturn's service responsible for processing the transfer logs submitted by node operators (and, in the future, clients) and distributing the rewards accordingly. 

When a user requests a piece of content from Saturn's network, Saturn does not collect data from the user. Instead, Saturn takes the log of the retrieval directly from the node operator that served the request.

Since node operators are paid for the retrievals they provide, there is a clear attack vector where operators may change these logs to exploit the network and collect a bigger share of the rewards being distributed.

As such, the Treasury needs to make sure that node operators receive the right incentives and that we are capable of detecting fraudulent logs and penalizing the misbehaved operators.

The diagram below illustrates the structure of the Treasure service:


<div style="text-align:center">
<img width="400" src="https://github.com/protocol/cel-retrieval/blob/master/saturn-aliens/reports/images/treasury_diag.drawio.png?raw=true">
<br>
<br>
</div>


The Treasury receives data from the [logs service](https://www.notion.so/pl-strflt/Logs-service-d52cb0fd0bff4c3392fc765720d10b81) and begins by processing it in the log detection module. The log detection module is responsible for flagging the logs and operators that look suspicious and sending these flagged entities to the reward distribution module.

The approach for the log detection module will be to start with simple detection techniques (e.g. heuristics and simple anomaly detection). Then, as we collect more data from Saturn and gain experience from real users, we will iterate and improve the detection model.

Next, the reward calculator is the part responsible for processing transfer logs and other metrics, and computing how much FIL each node operator will receive. This is the part of the Treasury that will define the main incentives for node operators and guarantee that operators are aligned with the long-term vision and goals for Saturn.

Finally, underlying all the components, we have the monitoring module. Because Saturn will function in an agile/iterative setting, we need to be able to monitor the entire payment process to improve both the log detection module and the reward calculator. We need to store the flagged entities and the payouts to operators.

In the next sections, we will describe in more detail the behaviors we want to incentivize/penalize and how each module contributes to this goal.


## Behaviors and incentives

### Good behaviors

At a high level, we wish to incentivize the following behaviors:

* High-bandwidth service
* Performance
* Reliability
* Geographical coverage
* Adherence to Saturn's design. Examples include L1s cache missing to L2s and L2s cache missing to SP's.

At the moment, measuring geographical coverage and adherence to Saturn's design will be tricky and, as such, it is out of scope for the Treasury release in October. We are noting the behaviors here for future iterations.

Thus, first three behaviors are used to design the formula for distributing rewards among Saturn nodes. Next, we discuss in more detail what each of the 3 behaviors entail and what metrics could be used to measure them.

**High-bandwidth service**

The most important behavior we want to incent is a service with high-bandwidth. Then main aim of a CDN is to serve content to users and, as such, the total amount of data (measured in bytes) delivered by Saturn in a given time interval should be as high as possible.

In addition, high bandwidth is expensive to maintain, which means it needs to be properly incentivized. As such, we aim to make bandwidth the metric with the most influence in rewards. 

We can collect the total data serve for each request from the transfer logs, and we can aggregate it by node to get the total bandwidth served by the node in a give time interval.

**Performance**

The second most important behavior we want to incentivize is performance. By this we mean the nodes should fulfill requests in such a way that leads to a good experience for clients. With this in mind, the two most important metrics are:

* Time to first byte (TTFB) - how quickly the first requested byte arrives at the client. TTFB measures how quickly the node responded to the request. This metric will be initially estimated by Saturn using generated traffic. Then, once we start integrating clients, we can use the client's logs to estimate TTFB.
* Download speed - how quickly the client downloads all the requested. Download speed measures how long it took for node to fulfill the request and, thus, how long the user had to wait to receive the full content. The metric can be taken from the transfer logs using the column `request_duration_sec`.

Note that download speed is often limited on the client's end. In other words, a node may often be able to upload content to a client at 100Mbps, but the node may be on a cellular connection and is only able to download content at 20Mbps. 

There are other metrics we could use to measure performance such as cache hit ratio. However, here we are focussing on what *actually* matters to end users, which is TTFB and total download speed. In the cache hit ratio example, the higher the cache hit ratio, the lower the TTFB will be, which is the metric already being rewarded.


**Reliability**

Nodes leaving the network degrade the network performance and experience for users. For example, when a node goes down, it can take up to 60 seconds for that node to be detected as down and removed from the network. Saturn's service worker can recover gracefully, albeit with degraded performance. Dumb clients without ARC's service worker can't, and their requests may fail.

As such, we want to introduce a mechanism for nodes to gracefully tell the network they will be going offline. If a node goes offline not gracefully, we need to penalize the node. If it goes offline gracefully, we still want to penalize it, although less than going ungracefully.

We can currently extract the uptime data of each station from the orchestrator. This is trusted data since the service is operated centrally and the data is not reported by nodes.

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

In opposition to good behaviors, bad behaviors will be used to penalize nodes. The log detection module will be responsible for detecting the behaviors. After a specific log or node is flagged, there are different ways that we can penalize bad-behaving nodes:

* Remove fraudulent logs, reducing the reward to the corresponding node
* Apply a penalty to the total reward the node
* Reduce the node's future rewards by limiting the requests it is able to serve

## Log detection module

The log detection module aims to detect any doctored or fake logs submitted by node operators. Since the initial version of the Treasury service has to be designed before Saturn has real active users, we start with a simple heuristics-based detection system, tuned with sensible assumptions about how users will operate with Saturn and the testing data we already have.

After Saturn is launched and more data is collected, we plan to iterate on this simple system by improving the heuristics and experimenting with more sophisticated detection methods such as anomaly detection models, supervised models, and active learning models.

Independently of the detection method, when we talk about fraudulent behavior, there are two separate levels at which we can detect it:

1. **Request level:** Level where we look at individual logs, which corresponds to detecting specific requests that do not look legitimate. An example here would be a request that has an impossibly fast duration. At this level, we screen all the individual requests coming from the logs service and flag any that look suspicious. The output is a list of flagged requests and the origin of their flags.
2. **Station level:** Level where we do not pinpoint a specific log that looks fraudulent but, instead, we look at the general behavior of individual node operators. An example here would be a node operator that is logging an impossibly high number of requests. At this level, we aggregated the raw logs for each operator and flag any that looks suspicious. The output is a list of flagged operators and the origin of their flags.

### Heuristics

Heuristics are defined as simple rules that encode a specific behavior we are trying to avoid. In this module, we will have heuristics for the two levels described before - requests and node operators.

Most heuristics have a threshold that needs to be set or tuned. This threshold depends on a single metric that we are comparing against. For instance, if we had a *fast requests* heuristic that aimed to catch operators that were reporting impossibly high TTFB values, the metric would be TTFB, and we would need to set a threshold on this metric to encode what is "impossibly high".

We can interpret this problem as a search for univariate anomalies or outliers. In the case of the *fast requests* heuristic, we are interested in data points that are too small for the *"normal"* data distribution. Here, the threshold is the point below which we consider a data point *"abnormal"*.

There are two ways one can go about setting these thresholds:

1. **Expert judgment:** here we use our knowledge of how Saturn and real requests work to set the threshold. This may be useful for cases where we can easily define what is *impossible*.
2. **Statistical outliers:** here we use real data from Saturn to model the statistical distribution of the underlying metric. This assumes that the data we have is "normal" and will be representative of future requests. Once we have the empirical distribution for the metric, we can set the threshold such that, with a certain statistical significance, all points falling outside are sampled from a different distribution.

In the end, we use a mixture of the two strategies.

More details about the heuristics and the log detection module in general, can be found in a [dedicated report](https://hackmd.io/@cryptoecon/SJIJEUJbs/%2FWihFXzN9QteSwIxHW5zKeQ).

## Reward calculator 

The reward calculator is the module responsible to computing the payouts to node operators. There are 5 main principles we used to design the module:

1. Simplicity over complexity → we only add complexity if it serves a purpose and, thus, we try to build the simplest process that achieves the goal.
2. Bounded rewards → since we are still in a testing phase, we should limit the daily rewards to avoid overspending in case of DDoS attacks and other anomalous behavior.
3. Incent a reliable and performant service → these are the two main attributes we care about when designing incentives. First, we want operators to serve a high volume of retrievals with a fast download time. Retrieval volume is measured by the total bytes served in a given time interval, while the download time is measured as the time-to-first-byte (TTFB) and total download time. Second, we want operators to be reliable and fail gracefully (this is more important for L1s than L2s).
4. Incent honesty → Operators should be incentivized to report their own faults and be truthful about their own logs
5. Preference towards free market → we try to leverage free market mechanics and supply-demand to avoid having to set a price for content delivery. Because we don't know the real costs Saturn nodes will incur when running Saturn, we need to allow for some price discovery. Price setting on new services is a hard problem and letting the market decide on the market is a good design for when we have price uncertainty. 

More details about the final reward distribution functions and their impact on rewards can be found in a [dedicated report](https://hackmd.io/@cryptoecon/SJIJEUJbs/%2FMqxcRhVdSi2txAKW7pCh5Q).

## Annex

### Saturn architecture

![](https://github.com/protocol/cel-retrieval/blob/master/saturn-aliens/reports/images/saturn_arch.png?raw=true)
<div style="text-align:center">
<em>Saturn M1 architecture</em>
</div>

### ARC payout pipeline

1. Nodes send property session and p2p transfer reports to the log ingestor. Property session reports are how long a node was on a given website and p2p transfer reports are how much data was sent from one node to another.
2. Log ingestor sanity checks, but does not perform fraud detection, on these reports. Sanity checked reports are written to google BigQuery.
3. Once a day, every day, the bookkeeper runs. The bookkeeper is a python script that runs through all the logs in BigQuery and:
   1. Does basic fraud detection. Irregular reports are dropped
   2. After fraud detection, calculates earnings + charges and writes those calculation results to a separate BigQuery table
   3. Issues payouts and charges customers based on the results of the above calculations.
   4. The bookkeeper writes results to a table:
      1. to leave a paper trail, and 
      2. so payouts and charges can be re-run in the future if things break or fail for any reason
4. The bookkeeper submits payouts to PayPal and sites get paid. If the bookkeeper already paid out a given site for a day (based on non-null db records), that site won't get paid again. This allows us to re-run the bookkeeper at any time to issue any outstanding, or failed, payments.
5. The bookkeeper submits charges to stripe and customers get charged.
