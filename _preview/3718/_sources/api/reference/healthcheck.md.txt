# Django Healthcheck

The Django API healthcheck endpoint checks the following:

- Whether the API is accessible at all (i.e., is Django returning responses)
- Whether the Postgres database is accessible to Django, by checking if
  connections are available to the database
- Optionally, whether Elasticsearch is accessible to Django (only when the
  `check_es` query parameter is present)
  - When debugging live healthcheck requests, check the request parameters to
    determine whether Elasticsearch health is included

The healthcheck can fail for any of the following reasons:

- The worker never started and therefore Django is unable to handle requests
- The worker meant to service the healthcheck request was aborted, either
  because it timed out when serving another or this request, or because the
  entire task was stopped due to another failure
- The database connection health check failed, either due to a temporary or
  persistent database connection issue
- The `check_es` query parameter was passed and the worker was unable to
  establish a connection to Elasticsearch _or_ Elasticsearch reported cluster
  health as "red"
