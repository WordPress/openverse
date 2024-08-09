# Running frontend tests

Once you've made some changes to the codebase, it is important to run tests.
Openverse uses unit tests, Playwright tests for end-to-end, and visual
regression testing of the app and Storybook components. This guide will help you
run the tests. To learn more about how to test PRs, Playwright tests and
Storybook visual regression tests read the
[testing guidelines](/frontend/reference/testing_guidelines.md).

## Steps

1. Ensure you've gone through the
   [quickstart guide](/frontend/guides/quickstart.md).

2. Run unit tests for the frontend.

   ```bash
   ./ov just frontend/run test:unit
   ```

   ````{note}
   Unit tests are automatically run by pre-commit before Git push, if you've set
   up pre-commit's Git hooks by running the following command.

   ```bash
   ./ov just precommit
   ```

   ````

3. Run the Playwright tests. This will run both the end-to-end tests and the app
   visual regression tests.

   ```bash
   ./ov just frontend/run test:playwright
   ```

4. Run the Storybook visual regression tests.

   ```bash
   ./ov just frontend/run test:storybook
   ```

   ````{note}
   This will run the Storybook visual regression tests inside a docker container. Should you wish to run the
   tests locally, you can use the command below. However, please note that unless
   you are running the same operating system (down to the distro, in some cases)
   there are likely to be visual rendering differences that will cause snapshot
   tests to fail on false-positives.

   ```bash
   ./ov just frontend/run test:storybook:local
   ```

   ````

## Updating snapshots

If you've made changes to the frontend that require updating snapshots, you can
run both the playwright and storybook tests with the `-u` flag. For example,
this will update the snapshots for the app visual regression tests:

```bash
./ov just frontend/run test:playwright visual-regression -u
```

This will similarly update the storybook snapshots:

```bash
./ov just frontend/run test:storybook -u
```
