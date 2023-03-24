# Analytics

Analytics on the frontend requires the Plausible setup to be up and running.

## Starting up

Bring up the Docker services needed by the frontend. This includes Plausible and
the PostgreSQL and Clickhouse databases it needs.

```console
$ just frontend/up
```

The `frontend/up` recipe orchestrates the following services: `plausible_ch`,
`plasible_db` and `plausible`.

Now you should be able to access the following endpoints:

- the Plausible UI on [http://localhost:50288](http://localhost:50288)

## Shutting down

Refer to the [common instructions](../quickstart.md#shutting-down).
