# Django Healthcheck

The Django API healthcheck endpoint checks the following:

- Whether the API is accessible at all (i.e., is Django returning responses)
- Optionally, whether the Postgres database is accessible to Django, by checking
  if connections are available to the database (only when the `check_db` query
  parameter is present)
- Optionally, whether Elasticsearch is accessible to Django (only when the
  `check_es` query parameter is present)
  - When debugging live healthcheck requests, check the request parameters to
    determine whether the database or Elasticsearch health is included

The load balancer and container health checks pass neither parameter. The
database check needs a connection from the per-task pool, so when slow requests
exhaust the pool the check times out as well and the task is killed, which only
shifts the load onto the remaining tasks. A task that cannot reach the database
never finishes starting anyway, because migrations run on startup.

The healthcheck can fail for any of the following reasons:

- The worker never started and therefore Django is unable to handle requests
- The worker meant to service the healthcheck request was aborted, either
  because it timed out when serving another or this request, or because the
  entire task was stopped due to another failure
- The `check_db` query parameter was passed and the database connection health
  check failed, either due to a temporary or persistent database connection
  issue
- The `check_es` query parameter was passed and the worker was unable to
  establish a connection to Elasticsearch _or_ Elasticsearch reported cluster
  health as "red"
