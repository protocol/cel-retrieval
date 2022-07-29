---
title: Saturn rewards design - Team discussion
tags: Saturn aliens
description: Slides for supporting the discussion about how to design Saturn's reward distribution
breaks: false
type: slide
---

<style>
.reveal {
  font-size: 32px;
}
</style>

# Saturn's reward distribution design
## Discussion with Saturn Team
### August 2022

[![Generic badge](https://img.shields.io/badge/Slides%20on%20HackMD-WIP-1abc9c.svg)](https://hackmd.io/@msilvaPL/BJiZq5Anc)

---

## High-level goal

**Reliable** network capable of serving **X total bandwidth** per day with an average **TTFB of Y**

----

### Comments:

- Change the concept of bandwidth
- Should we use number of retreivals or total bandwidth? Bandwidth is what we care the most
- Some CDNs charge per request, while other charge per bandwidth (https://aws.amazon.com/cloudfront/pricing/)
- Using number of requests is easier to game than total data sent
- Currently Saturn is serving 100TB per day & 120M requests/day (this is done with syntetic load) -> we are trying to match the IPFS gateway load

---

## Design principles

1. Simplicity over complexity
2. Bounded rewards (i.e. having a pool of rewards)
3. Preference towards free market (on the seller side)
4. Incent a reliable and performant service, with honest operators

----

### Comments:

- We agree to have an initial pool of rewards
- We already have a set of operators that want to participate
- How will we fund Saturn? At we start we need to fund it ourselves.
- How big is the pot of FIL? How much is need for 100 nodes?
- would it make sense to integrate ARC? We can but it is not a priority
- We think about having a  price for custumers. Some clients want to know the price and it should be simple
- Saturn is not peer-to-peer and there are no single deals
- Maybe we need to have a price breakdown per region. Some regions are more expensive (https://aws.amazon.com/cloudfront/pricing/)


---

## Question #1 - L1 vs L2

Do we want to differentiate rewards for L1s and L2s?

----

### Comments:

- Yes. The costs are difference. L2 are home users while L1s are big servers
- L2s will be happy to receive 10 $ per month
- L1s have a different scale and thus need to receive more
- L2s will not take action to improve their performance
- Uptime is not as important for L2s. They should be freer to leave the network
- L1s need to guarantee service
- In the logs, it will be clear who is an L1 and who is an L2
- Fake log entries are the main attack vector

---

## Question #2 - Available data

- What data will we receive from L1s and L2s?
- Can we have L1s reporting the performance of their L2 swarm?
- Can we collect info on what requests L1s are sending to their swarms?
- Do we collect get the geolocation of all nodes?

----

### Comments:

- tbd

---

## Question #3 - Client data

Do we expect to collect any data from clients?

----

### Comments:

- When we integrate clients, we will have data from clients.
- However, right now we don't have clients so we will not have this data
- We can use ARC as the first client to get this data
- We can use ARC to measure TTFB
- Although clients can still cheat and generate fake data

---

## Question #4 - Swarm interactions

Should L1s be liable for the faults of their swarm?

----

### Comments:

- No, it should not be their fault
- We want to keep it trustless

---

## Question #5 - Actor actions

What actions can L1s and L2s make?

- Entering and leaving the network
- Increasing/decreasing their bandwidth and cache
- Cheat -> fake logs
- Attacking other nodes (e.g. fake load on competitors to get them kicked-out)
- L2s can change their geography

----

### Comments:

- We will have info on what is their committed capacity
- L1s and L2s are not really "commiting" resourecs. They are stating the max capacity that they can serve

---

## Question #6 - Incent service - used vs available

Do we want to incent actual service or offered service?

Do we want to reward the actual bandwidth delivered (which depends on the clients and other external factors) or do we want to reward the bandwidth the Operator is capable of providing?

----

### Comments:

- It should be actual service. Operators willl bring new people to the network
- We don't want to pay for resoirces that are not used (.e.g geographies)
- There is a possible issue of operators getting paid less because the client's download is bad
- Maybe we can do an hybrid model where some rewards come from actual service and the other part come from available service