# Storybook tests

We run Playwright tests for our Nuxt application. We also run them for Storybook, where components are tested in isolation and (ideally) in a comprehensive way that is not always possible inside an actual application.

Generally it is preferrable to write regular Jest tests with `@testing-library/vue`, however, some interactions require a real web browser context (like loading audio files, testing drag and drop interactions, etc). For these, Playwright is the perfect tool. We can also use Playwright to write visual regression tests for components in isolation so that we don't have to dupliate things like focus state testing into our application level tests.

Our Nuxt playwright tests are described by the [README in the `playwright` test directory](../playwright/README.md). Please see the section on "Dockerization" as it also applies to the Storybook tests.

## Running the tests

To run the tests:

```bash
pnpm test:storybook
```

This will run the tests inside a docker container. Should you wish to run the tests locally, you can use the following:

```bash
pnpm test:storybook:local
```

But please note that unless you are running the same operating system (down to the distro, in some cases) there are likely to be visual rendering differences that will cause snapshot tests to fail on false-positives.

## Writing tests

It is preferrable to write tests using the iframed version of the component to avoid Storybook UI updates from effective snapshots. To access this, take the `path` query parameter for any story and apply it to the `/iframe.html` route. See [`v-checkbox.spec.ts` for an example](./visual-regression/v-checkbox.spec.ts).

### Codegen

You can use Playwright's `codegen` tool to generate tests. For this you will need to run Storybook locally on your own using `pnpm storybook`. Then run:

```bash
pnpm test:storybook:gen
```

Please note that the codegen script automatically runs against the non-iframed version of storybook, so while you can record interactions and use the resulting script, you will likely need to adapt it for running inside the iframed version of the page in the actual test.
