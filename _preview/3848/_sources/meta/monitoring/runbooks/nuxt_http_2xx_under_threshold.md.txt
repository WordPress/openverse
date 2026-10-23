# Run Book: Nuxt 2XX responses count under threshold

```{admonition} Metadata
Status: **Stable**

Alarm link:
- [Alarm details](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+HTTP+2XX+responses+count+under+threshold)
- [ECS-Production-Dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
```

## Severity guide

Confirm there is not an outage.

Check if the overall request count has decreased as well (this can be confirmed
via the
[CloudWatch dashboard](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/ECS-Production-Dashboard)
or in Cloudflare).

- If the overall requests have decreased, the severity is low. But you should
  continue to investigate why the usage has decreased below the usual amount.
- If the overall requests have not decreased, a large number of those requests
  must be returning non-2XX responses, which is high severity. Further
  investigation is warranted to determine the cause for the non-2XX responses.

## Historical false positives

Nothing registered to date.

## Related incident reports

Nothing registered to date.
