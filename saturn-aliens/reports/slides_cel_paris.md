---
title: Saturn aliens - CEL Paris colo 07-2022
tags: Saturn aliens
description: Slides for supporting the discussion about the Saturn Aliens project with CEL
---

<style>
.reveal {
  font-size: 32px;
}
</style>



# Saturn aliens
## CEL Paris colo
### July 2022

---

## Session goals

- Present Saturn Aliens and its goals
- Show what has been done so far
- Discuss some econ designs

---

# Saturn overview

---

![](https://i.imgur.com/DONZ3kC.jpg)

---

<div style="text-align:center">
<img width="700" src="https://i.imgur.com/iThGfgp.png">
</div>

*Credit to Patrick Woodhead*

---

## Saturn roadmap

- Q2 2022
    - Private test network of L1 nodes. Beat IPFS Gateway performance.
- Q3 2022
    - Open, public network of L1 nodes. Test network of L2 nodes.
- Q4 2022
    - Connect L1s to L2s and L2s to Storage Providers (SPs), end-to-end.
- Q1 2023
    - Adopt first network-wide Cryptoeconomics model.

---

## Saturn aliens

Main goal is to design V1 of **Saturn's Treasury** for public Q3 launch

### &darr;

Service responsible for processing the logs submitted by node operators and distributing the rewards accordingly.

---

## Behaviors and Incentives

- Good behaviors:
    - Performance
    - Reliability
    - Geographical coverage
    - Adherence to Saturn's design (out of scope for Q3)

- Bad behaviors:
    - Doctored logs
    - Fake retrievals (bots)
    - Retrievals with incorrect content


---

## Saturn Treasury

<div style="text-align:center">
<img width="490" src="https://i.imgur.com/WJehybq.png">
<br>
<br>
</div>

---

## Fraud detection module

- Current plan:
    - Start with simple heurisics
    - Explore anomaly detection
    - Iterate when we have real user data (after Q3 launch)


###### Full list of heuristics can be found in the [spec document](https://hackmd.io/@msilvaPL/r1YWCz4j9)

---

## Reward Distribution

- Ansgar proposal: apply multipliers to a base function. Multipliers are defined based on some targets we wish nodes to achieve
    - Base reward is a function of FIL to bytes served
    - Multiplier based on time-to-first-byte (TTFB)
    - Multiplier based on total download time

---

## Discussion topics

- Some open questions:
    - How to penalize flagged nodes?
    - How to incorporate reliability?
    - How to incorporate geographical coverage?
    - Should we reward average behaviors?

---

# Thank you!

- [GitHub repo](https://github.com/protocol/cel-retrieval)
- [Issues](https://github.com/protocol/cel-retrieval/issues)
- [Treasury specification](https://hackmd.io/@msilvaPL/r1YWCz4j9)
- [Saturn website](http://strn.network/#start)

---

## Main takeaways from discussion (Part 1)

- We cannot guarantee profitability for station operators!
- Can we use an auction model? Instead of setting a fixed price by byte, we can split a pot of rewards among the participants and let the market set the price.
- Are behavior scores multiplicative or additive? If we have a very high TTFB, do we ignore the other behaviors?
- Do we care about actual service or guaranteed service?

---

## Main takeaways from discussion (Part 2)

- We can have a mechanism similar to Filecoin gas fee where we increase and decrease the rewards pot based on how the network is behaving
- We need to figure out how to incentive honesty and fault reports. Maybe ramp up penalties based on repeating offenses?
-  We can have different pools of rewards for each behavior and let content publishers fund each pool based on what behaviors they are interested in.
