# Run Book: API Production HTTP 2XX responses count under threshold

```{admonition} Metadata
Status: **Stable**

Alarm links:
- [Alarm details](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Production+HTTP+2XX+responses+count+under+threshold?)
- [ECS-Production-Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
- [Production Database + Elasticsearch dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/Service-Overview)
```

## Severity Guide

After confirming there is not a total outage, check if the overall request count
has decreased as well (go to the [CloudWatch dashboard][cloudwatch] or
alternatively check in CloudFlare). If the overall requests are lower then the
severity is low, and you should continue searching for the cause of the general
decrease.

If the lower number is only in 2XX responses the severity is likely high, so
also check the dashboard to look for other anomalies. Go to the [API
logs][api_logs] to check for errors or data that yield clues.

[cloudwatch]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard
[api_logs]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fproduction$252Fapi

## Historical false positives

Nothing registered to date.

## Related incident reports

Nothing registered to date.
