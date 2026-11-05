# Run Book: Nuxt Production Average Response Time above threshold

```{admonition} Metadata
Status: **Stable**

Alarm link:
- [Alarm details](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+Average+Response+Time+above+threshold)
- [ECS-Production-Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
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

To gather more information check the [log group][log_group], use the "Logs
Insights" view to query for requests that may be taking longer than expected
with a CloudWatch query similar to the following which can give more hints about
which routes are causing increased response times. Occasionally the `/api/event`
endpoint will take longer to respond (due to upstream issues with Plausible),
and these cases will increase our average response time while not actually
affecting frontend performance for users. The following query shows the top 10
routes where the request took longer than 0.5 seconds grouped by number of
requests made to that route.

```
fields request, request_time, @timestamp, @message
| filter request_time > 0.5
| stats count(*) as request_count by request
| sort request_count desc
| limit 10
```

[traffic_runbook]:
  /meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md
[log_group]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fproduction$252Ffrontend

## Historical false positives

- _2024-04-10, 22:00 UTC_: Requests to the `/api/event` endpoint were taking
  longer than expected and impacted average response time, but not normal
  frontend traffic response time.

## Related incident reports

- 2023-06-13 at 03:50 UTC: Frontend increased response times (reason unknown)
