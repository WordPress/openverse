# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Steps

1. Ensure you've gone through the [quickstart guide](../quickstart.md). Ensure
   that the Docker daemon is running.

2. Run the tests.

   ```console
   $ just api/test
   ```

   ```{note}
   Since the tests are executed inside Docker, Python dependencies need not be
   installed.
   ```
