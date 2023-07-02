# Stable Run Book Sample

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

## Run Book: Increased search response time

```{admonition} Metadata
Status: **Stable**

Alarm links:
- Alarm page: <https://example.com/aws/us-east-1/Openverse/CloudWatchAlarms/increased-search-response-time>
- API dashboard: <https://example.com/aws/us-east-1/Openverse/CloudWatchDashboards/production-api>

Configured downtime:
- 18:00 UTC - 03:00 UTC due to organic traffic decreases creating low-confidence standard deviation values
```

### Severity Guide

After confirming there is not a total outage, you need to identify the source of
the slowdown. Historically the source of response time increases have been
issues in dead link filtering. Check for dead link timing first and foremost and
check for increased 5xx responses on the route that may indicate issues with
completing the dead link process.

After that, check Elasticsearch pagination and total query time per search
endpoint request to confirm that those are stable.

Finally, check that Postgres response times and CPU usage are stable.

If none of these are abnormal or are only slightly higher, this is probably
caused by an organic increase in traffic. Consider scaling the API by one task
if the increase is substantial and sustained, otherwise investigate traffic
origin according to the _traffic analysis run book_ and identify potential
sources of organic traffic increases (conferences, etc).

### Related incident reports

- _2023-06-08 at 03:00 UTC: Something broke, oh dear!_
- _2023-08-03 at 17:00 UTC: Something broke less badly, oh dear._
