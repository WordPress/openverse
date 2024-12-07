# Runbooks

This section collects runbooks for responding to Openverse infrastructure
alarms.

Please see
[the "Run Books" section of the ECS baseline monitoring implementation plan for further details on what runbooks are and their requirements](/projects/proposals/monitoring/20230606_implementation_plan_ecs_alarms.md#run-books).
The implementation plan also includes
[example runbooks](/projects/proposals/monitoring/20230606_implementation_plan_ecs_alarms.md#example-run-books)
that can be a good resource when writing a new one.

```{toctree}
:titlesonly:

api_http_2xx_under_threshold
api_http_5xx_above_threshold
api_avg_response_time_above_threshold
api_avg_response_time_anomaly
api_p99_response_time_above_threshold
api_p99_response_time_anomaly
api_request_count_anomaly
nuxt_http_2xx_under_threshold
nuxt_http_5xx_above_threshold
nuxt_avg_response_time_above_threshold
nuxt_avg_response_time_anomaly
nuxt_p99_response_time_above_threshold
nuxt_p99_response_time_anomaly
nuxt_request_count_anomaly
unhealthy_ecs_hosts
```
