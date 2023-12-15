# Run Book: API Production HTTP 5XX responses count above threshold

```{admonition} Metadata
Status: **Stable**

Alarm links:
- [Alarm details](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/API+Production+HTTP+5XX+responses+count+over+threshold)
- [API Production log group][log_group]
- [ECS-Production-Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
- [Production Database + Elasticsearch dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/Service-Overview)
```

## Severity Guide

After confirming there is not a total outage, check if the increase of 5XX HTTP
errors is related to a regular time where resources are expected to be
constrained like a recent deployment, a data refresh, DB maintenance, etc. If
the spike is related to one of these events and the alarms stabilizes in the
short time then the severity is low.

If the issue is not related to known recurrent events and persists, the severity
is critical. Check if dependent services –DB, Redis, Elasticsearch– are
available to the API or if the problem is intrinsic to itself. To gather more
information check the [log group][log_group], use the "Logs Insights" view to
query for requests that failed using a CloudWatch query similar to the following
which can give more hints about where is the problem.

```
fields request, @timestamp, @message
| filter status >= 500
| sort @timestamp desc
| limit 20
```

[log_group]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fproduction$252Fapi

## Historical false positives

Nothing registered to date.

## Related incident reports

- _2023-07-16 at 05:05 UTC: 5XX responses spike to ~50 near a database restart
  during the RDS maintenance window. Unknown cause._
