# Unstable Run Book Sample

```{tip}
A real run book should include links to anything relevant like
dashboards the maintainer should check. This example does not do
so for the sake of simplicity. Italicised terms identify places
that should be linked.
```

```{caution}
The information and instructions in this sample are completely
fictional and should be taken as true-to-life documentation of our
services or how to respond to incidents. It may also refer to
observable metrics that we do not actually have configured for
our services.
```

```{note}
The [explanation of source order](#explanation-of-source-order) section
serves as an example of "additional information" that may be relevant.
Run books will inevitably need to document domain knowledge of our services
and implementation details as these are often of critical importance
when understanding performance issues especially. The overall guide should seek
to be a consice list of steps, but should link to internal additional sections
or external documentation that will help run book users make the judgements
required by the run book.
```

## Run Book: Increased search response time

```{admonition} Metadata
Status: **Unstable**

Maintainer: @octocat

Alarm links:
- <https://example.com/aws/us-east-1/Openverse/CloudWatchAlarms/increased-search-response-time>
```

### Severity Guide

After confirming there is not a total outage, you need to identify the source of
the slowdown. There are three general potential sources of search slowdown, in
[order of likelihood](#explanation-of-source-order):

- Elasticsearch
- Python
- Postgres access

Therefore, check the following, in order:

1. Request count and general network activity. If abnormally high, refer to the
   _traffic analysis run book_ to identify whether there is malicious traffic.
   If not, move on.
1. Average and p99 Elasticsearch response time. If stable, move on.
1. Total Elasticsearch time for a query (aggregated in Python for all pagination
   related activity for a single query). If high, query activity may have
   changed, either legitimately or illegitimately.
1. Parse query parameters from Nginx logs and check pagination and parameter
   count activity for abnormal or unexpected behaviour. If any exist, decide
   whether it is malicious or expected.
1. ... (and so on)

### Explanation of source order

Elasticsearch and Python have similar complexity on the search route. Postgres
is used for a single, rather straightforward query just before serialization.
Elasticsearch, however, is the most optimisable part of the search route and
also the part that can have unexpected interactions or stability due to related
activity like indexing during a data refresh.

### Historical false positives

- 2023-06-08 at 03:00 UTC. There was an increase in response time but it was
  brief and for a very short period of time and corresponded with peak traffic
  hourse. We think we can change the anomaly configuration to 2.5 standard
  deviations above the curve but we need further examples to corroborate this.
- 2023-06-12 at 16:00 UTC. This happened during low traffic when response time
  is also much lower than peak traffic. We think we might be able to add
  downtime for 13:00 to 20:00 UTC.

### Related incident reports

- _2023-06-08 at 03:00 UTC: Something broke, oh dear!_
- _2023-08-03 at 17:00 UTC: Something broke less badly, oh dear._
