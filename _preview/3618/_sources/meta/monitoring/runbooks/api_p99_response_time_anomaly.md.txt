# Run Book: API Production P99 Response Time anomaly

```{admonition} Metadata
Status: **Unstable**

Maintainer: @krysaldb

Alarm link:
- <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Production+P99+Response+Time+anomalously+high?>
```

## Severity Guide

To identify the source of the slowdown first check if there was a recent
deployment that may have introduced the problem, in that case rollback to the
previous version. Otherwise, check the following, in order:

1. Request count and general network activity. If abnormally high, refer to the
   [traffic analysis run book][traffic_runbook] to identify whether there is
   malicious traffic. If not, move on.
2. Check if dependencies like Elasticsearch or the database are constrained. If
   stable, move on.
3. Parse query parameters from Nginx logs and check pagination and parameter
   count activity for abnormal or unexpected behaviour. If any exist, decide
   whether it is malicious or expected.

[traffic_runbook]:
  /meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md

## Historical false positives

Nothing registered to date.

## Related incident reports

- 2023-09-01 at 18:10 UTC: Increased API response times over filtered image
  index recreation
