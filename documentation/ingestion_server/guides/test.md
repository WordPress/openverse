# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Steps

1. Ensure you've gone through the
   [quickstart guide](/ingestion_server/guides/quickstart.md). Ensure that the
   Docker daemon is running.

2. Install the Python dependencies, including dev-dependencies.

   ```console
   $ just ingestion_server/install
   ```

   ```{caution}
   If you experience error installing `psycopg2`, refer to the documentation
   about the [OpenSSL prerequisite](/general/general_setup.md#openssl).
   ```

3. Run the integration tests.

   ```console
   $ just ingestion_server/test-local
   ```
Note that if an `.env` file exists in the folder you're running `just` from, it may
interfere with the integration test variables and cause unexpected failures.

## Making requests

To make cURL requests to the server

```bash
pipenv run \
  curl \
    --XPOST localhost:8001/task \
    -H "Content-Type: application/json" \
    -d '{"model": <model>, "action": <action>}'
```

Replace `<model>` and `<action>` with the correct values. For example, to
download and index all new images, `<model>` will be `"image"` and `<action>`
will be `"INGEST_UPSTREAM"`.