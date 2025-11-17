# Testing guide

Once you've made some changes to the codebase, it is important to run tests.

## Steps

1. Ensure you've gone through the [quickstart guide](../quickstart.md).

2. Run unit tests for the frontend.

   ```console
   $ just frontend/run test:unit
   ```

   ````{note}
   Unit tests are automatically run by pre-commit before Git push, if you've set
   up pre-commit's Git hooks by running the following command.

   ```console
   $ just precommit
   ```

   ````
