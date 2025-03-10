# Run Book: Nuxt Production P99 Response Time anomalously high

```{admonition} Metadata
Status: **Disabled** until Nuxt request logging is added.

Maintainer: @obulat

Alarm link:
- <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+P99+Response+Time+anomalously+high>
```

## Severity Guide

Confirm that there is not a total outage of the service. If not, the severity is
likely low. Check for the request count and general network activity. If
abnormally high, refer to the [traffic analysis run book][traffic_runbook] to
identify and block any malicious traffic. If not, then check for a recent
deployment that may have introduced a problem, and [rollback][rollback_docs] to
the previous version if necessary.

[traffic_runbook]:
  /meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md
[rollback_docs]: /general/deployment.md#rollbacks

## Historical false positives

Nothing registered to date.

## Related incident reports

Nothing registered to date.
