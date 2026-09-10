# Run Book: Nuxt 5XX responses count above threshold

```{admonition} Metadata
Status: **Stable**

Alarm link:
- [Alarm details](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+HTTP+5XX+responses+count+over+threshold)
- [Nuxt Production log group][log_group]
- [ECS-Production-Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
```

## Severity guide

Confirm there is not an outage.

Check if the connection to the API from Nuxt has been broken, which can result
in Nuxt returning 5XX errors.

If the connection is present and working, try to determine the source of the 5XX
errors (this can be checked by observing paths in the Cloudflare logs).

- If the API requests are returning 2XX responses, the severity is low. But you
  should continue to investigate the source of 5XX errors, which could be an
  external service like Plausible.
- If the API requests are returning 5XX responses, the severity is high. Further
  investigation into the API side is warranted to determine the cause for the
  5XX responses. Also refer to the
  [API 5XX runbook](/meta/monitoring/runbooks/api_http_5xx_above_threshold.md).
- To gather more information check the [log group][log_group], use the "Logs
  Insights" view to query for requests that failed using a CloudWatch query
  similar to the following which can give more hints about where is the problem.

```
fields request, @timestamp, @message
| filter status >= 500
| sort @timestamp desc
| limit 20
```

- Occasionally, we'll observe a high number of 5XX responses on the `/api/event`
  endpoint. These are often the result of outages or issues with Plausible and
  are not actionable for us. The following Log Insights query can be helpful in
  determining the source of the 500s based on the endpoints.

```
fields request, @timestamp, @message
| filter status >= 500
| sort @timestamp desc
| stats count(*) by request
```

[log_group]:
  https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fproduction$252Ffrontend

## Historical false positives

- _2024-04-02, 15:22 UTC_: High number of 500s to the `/api/event` endpoint,
  nothing actionable on our end.

## Related incident reports

- _2023-08-28, 12:06 to 12:24 UTC_:

  5XX responses spiked to ~591 due to Plausible degradation. This was not
  detrimental to UX.
