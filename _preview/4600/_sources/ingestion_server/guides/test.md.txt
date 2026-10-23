# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Ingestion tests

1. Ensure you've gone through the
   [quickstart guide](/ingestion_server/guides/quickstart.md). Ensure that the
   Docker daemon is running.

2. Install the Python dependencies, including dev-dependencies.

   ```bash
   ./ov just ingestion_server/install
   ```

   ```{caution}
   If you experience error installing `psycopg2`, refer to [documentation
   about the `psycopg2` build prerequisites](/general/general_setup.md#psycopg2-build-prerequisites).
   ```

3. Run the integration tests.

   ```bash
   ./ov just ingestion_server/test-local
   ```

   Note that if an `.env` file exists in the folder you're running `just` from,
   it may interfere with the integration test variables and cause unexpected
   failures.

## Making general test requests

To make cURL requests to the local server:

```bash
./ov just ingestion_server/curl-post '{"model": <model>, "action": <action>}'
```

Replace `<model>` and `<action>` with the correct values. For example, to
download and index all new images, `<model>` will be `"image"` and `<action>`
will be `"INGEST_UPSTREAM"`.
