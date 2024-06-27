# Ingestion server quickstart guide

This is the quick start guide for setting up and running the ingestion server
locally.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Starting up

Bring the ingestion server up, along with all their dependent services.

```bash
just ingestion_server/up
```

The `ingestion_server/up` recipe orchestrates the following services: `db`,
`upstream_db`, `es`, `indexer_worker` and `ingestion_server`.

Now you should be able to access the following endpoints:

- The list of ingestion jobs on
  [http://localhost:50281/task](http://localhost:50281/task)

You can view logs for the service using `ov just logs ingestion_server`.

## Shutting down

Refer to the [common instructions](/general/general_setup.md#shutting-down).
