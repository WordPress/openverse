# Run Book: Nuxt Request Count anomalously high

```{admonition} Metadata
Status: **Unstable**

Maintainer: @dhruvkb

Alarm link:
- [production-nuxt](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/Nuxt+Production+Request+Count+anomalously+high)
```

## Severity guide

[Identify traffic anomalies](/meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md)
in Cloudflare to determine if the increase is organic or due to a botnet.

- If the increase is organic, we must update our baseline expectation of our
  services' usages. The alarm thresholds should be updated if our services see
  higher usage frequently and consistently.
- If the increase is a botnet attack, we need to block these agents to restore
  usage to the usual level.

We also need to verify that the requests are being handled properly and that our
services are capable of meeting this demand (this can be observed from the CPU
and memory metrics in the ECS dashboards in CloudWatch).

- If our infra can handle the load, there is not much to do except continue to
  monitor that the resources stay within reasonable limits.
- If our infra cannot handle the load, we must scale our services by increasing
  capacity or adding more instances.

## Historical false positives

Nothing registered to date.

## Related incident reports

Nothing registered to date.
