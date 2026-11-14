# Run Book: API Production Request Count above threshold

```{admonition} Metadata
Status: **Unstable**

Maintainer: @krysaldb

Alarm link:
- <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Production+Request+Count+above+threshold?>
```

## Severity Guide

When a sudden increase in request count is noticed, verify that the services are
supporting the load by looking at metrics like response time or ES CPU usage for
example. If the API is doing fine, then severity is low and may only require
future resource scaling depending on the kind of traffic.

If the services are strained then the severity is critical, search for the root
cause to prevent more serious outages. If there are no recent obvious
integrations (like the Gutenberg plugin) then follow the run book to [identify
traffic anomalies in Cloudflare][runbook_traffic], to determine whether the
recent traffic is organic or if it comes from a botnet. Find the origin of
requests and evaluate whether it needs to be blocked or if Openverse services
need to adapt to the new demand.

[runbook_traffic]:
  https://docs.openverse.org/meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.html

## Historical false positives

Nothing registered to date.

## Related incident reports

Nothing registered to date.
