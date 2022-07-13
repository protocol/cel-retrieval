# Saturn Treasury specification

#### Maria Silva, July 2022

###### tags: `Saturn aliens`

***

**Table of contents**

[TOC]

***

## Overview

The Treasury is Saturn's service responsible for processing the logs submitted by node operators and distributing the rewards accordingly. 

When a client requests a piece of content from Saturn's network, Saturn does not collect data from the client. Instead, Saturn takes the log of the retrieval directly from the Station Operator that served the request.

Since Station Operators are paid for the retrievals they provide, there is a clear attack vector where station operators may change these logs to exploit the network and collect a bigger share of the rewards being distributed.

As such, the Treasury needs to make sure that Station Operators receive the right incentives and that we are capable of detecting fraudulent logs and penalizing the misbehaved operators.

The diagram below illustrates the structure of the Treasure service:


<div style="text-align:center">
<img width="490" src="https://i.imgur.com/4ftMJVs.png">
<br>
<br>
</div>


The Treasury receives data from the [logs service](https://www.notion.so/pl-strflt/Logs-service-d52cb0fd0bff4c3392fc765720d10b81) and begins by processing it in the fraud detection module. The fraud detection module is responsible for flagging the logs and operators that look suspicious and sending these flagged entities to the metrics aggregator module.

The approach for the fraud detection module will be to start with simple detection techniques (e.g. heuristics and simple anomaly detection). Then, as we collect more data from Saturn and gain experience from real users, we will iterate and improve the detection model.

Then, the metric aggregator combines the flags produced by the detection module with the raw logs and computes the metrics used to feed the reward calculator. The main output of this module is a table of metrics for each Station Operator, such as the total number of requests, total bandwidth, average request duration, station penalties for bad behavior, and so on.

Next, the reward calculator is the part responsible for processing the Station aggregated metrics and computing how much FIL each Station Operator will receive. This is the part of the Treasury that will define the main incentives for Station Operators and guarantee that operators are aligned with the long-term vision and goals for Saturn.

Finally, underlying all the components, we have the monitoring module. Because Saturn will function in an agile/iterative setting, we need to be able to monitor the entire payment process to improve both the fraud detection module and the reward calculator. We need to store the station aggregated metrics, the flagged entities, and the payouts to Station Operators.

In the next sections, we will describe in more detail the behaviors we want to incentivize/penalize and how each module contributes to this goal.


## Behaviors and incentives

:::warning
:warning: still need to align on whether we care more about some behaviors over the others and whether we are missing something
:::

Behaviors we want to incentivize:
* High bandwidth
* Fast retrievals
* Network growth
* Reliability


Behaviors we want to avoid:
* Doctored logs - creating logs of retrievals that didn't happen or changing real logs to improve some variables such as the bytes sent and the request duration.
* Fake retrievals - retrievals made by operators or other actors that do not correspond to real and lawful clients of the network.


## Fraud detection module

The fraud detection module aims to detect any doctored or fake logs submitted by station operators. Since the initial version of the Treasury service has to be designed before Saturn has real active users, we start with a simple heuristics-based detection system, tuned with sensible assumptions about how users will operate with Saturn and the testing data we already have.

After Saturn is launched and more data is collected, we plan to iterate on this simple system by improving the heuristics and experimenting with more sophisticated detection methods such as anomaly detection models, supervised models, and active learning models.

Independently of the detection method, when we talk about fraudulent behavior, there are two separate levels at which we can detect it:

1. **Request level:** Level where we look at individual logs, which corresponds to detecting specific requests that do not look legitimate. An example here would be a request that has an impossibly fast duration. At this level, we screen all the individual requests coming from the logs service and flag any that look suspicious. The output is a list of flagged requests and the origin of their flags.
2. **Station level:** Level where we do not pinpoint a specific log that looks fraudulent but, instead, we look at the general behavior of individual Station Operators. An example here would be a Station operator that is logging an impossibly high number of requests. At this level, we aggregated the raw logs for each Station Operator and flag any Operator that looks suspicious. The output is a list of flagged Station Operators and the origin of their flags.


### Heuristics

Heuristics are defined as simple rules that encode a specific behavior we are trying to avoid. In this module, we will have heuristics for the two levels described before - requests and Station Operators.

The next table describes all the heuristics proposed to be included in the detection system and highlights the reasoning for each heuristic. It is important to note that this is a first proposal and it is likely to change as the project matures.

| Name | Level | Description | Reasoning |
|:---:|:---:|:---:|:---:|
| High request count | Station | Flag operators with a total number of requests higher than a threshold | Operators may inject fake logs to bump their rewards. This rule catches operators that inject a massive number of requests |
| High bandwidth | Station | Flag operators with a bandwidth higher than a threshold | Operators may change their logs to bump their rewards. This rule catches operators where these changes add up to an impossibly high bandwidth |
| Bot client (requests) | Request | Flag the requests coming from a client whose total number of requests is higher than a threshold | Operators may employ bots to bump the number of requests and gain more rewards. this rule catches clients that have too many requests for a real user |
| Bot client (bytes) | Request | Flag the requests coming from a client whose total bytes transferred is higher than a threshold | Operators may employ bots to bump their bytes transferred and gain more rewards. This rule catches clients that are requesting too much data for a real user |
| Single client Stations (requests) | Station | Flag operators with an average request count per client higher than a threshold | Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total no. of requests divided by the number of clients will uncover some of these cases.  |
| Single client Stations (bytes) | Station | Flag operators with an average number of bytes transferred per client higher than a threshold | Operators may try to dodge detection by deploying bots on a small scale. If they use a small no. of bots, looking at their total bytes divided by the number of clients will uncover some of these cases.  |
| Self-requests | Request | Flag requests where the node ID and client ID are the same | Operators may try to do requests to themselves to collect more rewards. If they do, we can catch this by comparing the node ID with the client ID. |
| Doctored content (CID) | Request | Flag requests where the total bytes are higher than the threshold for the CID being requested | Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the CID that is being requested |
| Doctored content (referrer) | Request | Flag requests where the total bytes are higher than the threshold for the website being requested | Operators may change the total data being transferred in real requests to bump their rewards. This rule catches logs where the total bytes transferred is too high for the website that is being requested |
| Fast requests | Request | Flag requests where the duration is lower than a threshold (split by whether the cache is being used) | Operators may change the duration of real requests to bump their rewards. This rule catches logs where the request duration is too low for a comparable request (i.e., whether it uses cache or not) |

Almost all of the heuristics proposed have a threshold that needs to be set or tuned. This threshold depends on a single metric that we are comparing against. For instance, in the *fast requests* heuristic, the metric is the request duration. 

We can interpret this problem as a search for univariate anomalies or outliers. In the case of the *fast requests* heuristic, we are interested in data points that are too low for the *"normal"* data distribution. Here, the threshold is the point below which we consider a data point *"abnormal"*.

There are two ways one can go about setting these thresholds:

1. **Expert judgment:** here we use our knowledge of how Saturn and real requests work to set the threshold. This may be useful for cases where we can easily define what is *impossible*.
2. **Statistical outliers:** here we use real data from Saturn to model the statistical distribution of the underlying metric. This assumes that the data we have is "normal" and will be representative of future requests. Once we have the empirical distribution for the metric, we can set the threshold such that, with a certain statistical significance, all points falling outside are sampled from a different distribution.

Most likely, we will need to use a mixture of the two strategies, where we start with the statical distribution and then use expert judgment for further tunning.

:::info
:hammer: More details about the process and the final thresholds will be shared in a dedicated report -> Still **WIP**
:::



### Anomaly detection and ML 

:::info
:hammer: This section will be developed after the first draft is completed.
:::


## Metric aggregator module

As the name suggests, this module receives data from the logs service and the fraud detection module and computes some aggregations for each Station Operator. These aggregations will then feed the reward calculator.

The module starts from the raw logs. Then, it uses the outputs from the fraud detection module to filter all logs with a request-level flag. Afterward, the legit logs are aggregated by Station Operator and some metrics are computed, namely:

* Epoch
* Node ID
* Total number of requests
* Average bandwidth
* Total amount of bytes transferred
* Average request duration

Finally, the station-level flags reported by the fraud detection system are joined with the previous metrics, resulting in a new column for each station-level heuristic. This final table that contains the flags and the aggregated metrics for each Station is the outputs of the metric aggregator module.

:::warning
:warning: This list of metrics is likely to change as we design the reward calculator module
:::

## Reward calculator 

:::info
:hammer: **TBD:** waiting for alignment on behaviors and incentives
:::



## Annex

![](https://i.imgur.com/iThGfgp.png)
<div style="text-align:center">
<em>Saturn M1 architecture</em>
</div>


