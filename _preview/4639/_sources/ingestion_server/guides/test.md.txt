# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Ingestion tests

1. Ensure you've gone through the
   [quickstart guide](/ingestion_server/guides/quickstart.md). Ensure that the
   Docker daemon is running.

2. Install the Python dependencies, including dev-dependencies.

   ```bash
   ov just ingestion_server/install
   ```

3. Run the integration tests.

   ```bash
   ov just ingestion_server/test-local
   ```

## Making general test requests

To make cURL requests to the local server:

```bash
ov just ingestion_server/curl-post '{"model": <model>, "action": <action>}'
```

Replace `<model>` and `<action>` with the correct values. For example, to
download and index all new images, `<model>` will be `"image"` and `<action>`
will be `"INGEST_UPSTREAM"`.
