# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Steps

1. Ensure you've gone through the [quickstart guide](../quickstart.md). Ensure
   that the Docker daemon is running.

2. Install the Python dependencies, including dev-dependencies.

   ```console
   $ just ingestion_server/install
   ```

   ```{caution}
   If you experience error installing `psycopg2`, refer to the documentation
   about the [OpenSSL prerequisite](../general_setup.md#openssl).
   ```

3. Run the tests.

   ```console
   $ just ingestion_server/test-local
   ```
