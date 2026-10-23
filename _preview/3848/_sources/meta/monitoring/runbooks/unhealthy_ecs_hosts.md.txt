# Run Book: Unhealthy hosts for ECS service

```{admonition} Metadata
Status: **Stable**


Alarm links:
- [production-api](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/production-api+has+unhealthy+hosts)
- [staging-api](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/staging-api+has+unhealthy+hosts)
- [production-nuxt](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/production-nuxt+has+unhealthy+hosts)
- [staging-nuxt](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:alarm/staging-nuxt+has+unhealthy+hosts)
```

```{note}
This run book is shared between all unhealthy host count alarms _for ECS services_.
Our infrastructure is slightly different for non-ECS services so do not reuse this
run book for anything not deployed using ECS (though feel free to reference relevant
parts of it).
```

## Triage Guide

After confirming there is not a total outage, check the ECS events log for the
service. You can find a link to the events log for the specific service in the
additional information section of the alarm description included in the alert
notification. The events log can help you find the general cause for the
unhealthy hosts. Specifically, check whether the container failed to start
altogether or whether it starts but fails to respond to the healthcheck
requests.

If the container fails to start altogether (usually only after a deployment),
the severity is critical. Immediately
[roll the service back to the previous version](/general/deployment.md#rollbacks).
After kicking off the roll back,
[query the logs for the failed tasks](/meta/monitoring/cloudwatch_logs/index.md)
to check if there are logs that identify the problem preventing the container
from starting.

If the container fails the healthcheck request, determine whether this is a
persistent issue or just a blip. In a multi-worker service (like the Django
API), a single worker can fail a healthcheck without the entire service being
broken, for example, if that worker alone has difficulty establishing a database
connection due to DNS resolution issues. Follow the
[log querying guide](/meta/monitoring/cloudwatch_logs/index.md) to check whether
the cause of the timeout or failed healtcheck request is present.

A healthcheck failure is persistent if the ECS service continues to replace
tasks due to failed healthcheck requests. It is not persistent if the ECS
service eventually stops replacing tasks without intervention.

If the issue is persistent, the severity is critical. Check the logs for the
service and use information about service healthchecks to determine if services
checked by the healthcheck are failing:

- [Django API healthcheck](/api/reference/healthcheck.md)
- [Nuxt frontend healthcheck](/frontend/reference/healthcheck.md)

For example, if the Postgres database is failing to serve connections to the
API, the Django API service healthcheck will fail, causing the task to restart,
even though the core issue is with a dependent service.

If the persistent unhealthy hosts are caused by a related service, fix the
related service. Do not roll back the service with the unhealthy hosts until
you've confirmed that the healthcheck is no longer failing due to a related
service failure. For example, do not roll back the API if the healthcheck fails
due to a database connection issue unless the database connection issue is
confirmed to be an issue with the API and not the database.

```{hint}
If the persistent unhealthy hosts occur right after a deployment, you might be able to
"fast track" to the conclusion that the issue is with the newly deployed version rather
than a downstream service. However, coincidences do happen, so it's good practice to
consider whether downstream service changes coinciding with the new version deployment.
```

```{warning}
Recall that new deployments may also be the first time environment variable changes
are deployed. If a roll back does not help and it does not appear to be an issue with the
downstream service, then check whether environment variables changed for the service.

Database connection issues could be caused by a malformed connection string, for example.
```

If the unhealthy hosts are not persistent, then the severity is low. Record any
logs you can find for the unhealthy tasks in the incident report and triage
further investigation as usual.

## Historical false positives

None, yet.

## Related incident reports

None, yet.
