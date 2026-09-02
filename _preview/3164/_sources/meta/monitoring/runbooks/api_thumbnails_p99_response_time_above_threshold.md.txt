# Run Book: API Thumbnails Production P99 Response Time above threshold

```{admonition} Metadata
Status: **Unstable**
Maintainer: @stacimc
Alarm link:
- <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Thumbnails+Production+P99+Response+Time+above+threshold>
```

## Severity Guide

If the P99 response time is not [anomalously high][anomaly_alarm], the severity
is likely low. Check for a recent deployment that may have introduced the
problem, and rollback to the previous version. If not, check the request count
and general network activity. If abnormally high, refer to the [traffic analysis
run book][traffic_runbook] to identify and block any malicious traffic.

[anomaly_alarm]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Thumbnails+Production+P99+Response+Time+anomalously+high
[traffic_runbook]:
  /meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md

## Historical false positives

Nothing registered to date.

## Related incident reports

- 2023-09-05 at 22:15 UTC: Unhealthy thumbnail tasks restarted
- 2023-07-27 at 19:14 UTC: API Thumbnails unhealthy hosts
