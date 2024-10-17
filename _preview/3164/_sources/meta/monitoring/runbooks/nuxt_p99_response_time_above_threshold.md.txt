# Run Book: Nuxt Production Average Response Time above threshold

```{admonition} Metadata
Status: **Unstable**
Maintainer: @obulat
Alarm link:
- <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+P99+Response+Time+above+threshold?>
```

## Severity Guide

To identify the source of the slowdown first check if there was a recent
deployment that may have introduced the problem, in that case rollback to the
previous version. Otherwise, check the following, in order:

1. Request count and general network activity. If abnormally high, refer to the
   [traffic analysis run book][traffic_runbook] to identify whether there is
   malicious traffic. If not, move on.
2. Check if dependencies like the API or Plausible analytics are constrained. If
   stable, move on.

[traffic_runbook]:
  /meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md

## Historical false positives

Nothing registered to date.

## Related incident reports

- 2023-06-13 at 03:50 UTC: Frontend increased response times (reason unknown)
