# Storybook tests

We run Playwright tests for our Nuxt application. We also run them for
Storybook, where components are tested in isolation and (ideally) in a
comprehensive way that is not always possible inside an actual application.

Generally, it is preferable to write regular Jest tests with
`@testing-library/vue`, however, some interactions require a real web browser
context (like loading audio files, complex popover interactions, testing drag
and drop interactions, etc). For these, Playwright is the perfect tool.

We also use Playwright to write visual regression tests for components in
isolation so that we don't have to duplicate things like focus state testing
into our application-level tests. Sometimes, components cannot be tested in the
full app because they are shifted 1-2 pixels between the tests and therefore the
identical images do not match due to shifting.

You will find the functional component tests in `/test/storybook/functional`,
and visual regression tests that with snapshots in
`/test/storybook/visual-regression`

Our Nuxt playwright tests are described by the
[Playwright testing guide](./playwright_tests.md). Please see the section on
"Dockerization" as it also applies to the Storybook tests.

## Running the tests

To run the tests:

```bash
just frontend/run test:storybook
```

This will run the tests inside a docker container. Should you wish to run the
tests locally, you can use the command below. However, please note that unless
you are running the same operating system (down to the distro, in some cases)
there are likely to be visual rendering differences that will cause snapshot
tests to fail on false-positives.

```bash
just frontend/run test:storybook:local
```

## Writing tests

It is preferable to write tests using the iframed version of the component to
avoid Storybook UI updates from effective snapshots. To access this, take the
`path` query parameter for any story and apply it to the `/iframe.html` route.
See
[`v-checkbox.spec.ts` for an example](https://github.com/WordPress/openverse/blob/main/frontend/test/storybook/visual-regression/v-checkbox.spec.ts)

### Codegen

You can use Playwright's `codegen` tool to generate tests. For this you will
need to run Storybook locally on your own using `just frontend/run storybook`.
Then run:

```bash
just frontend/run test:storybook:gen
```

Please note that the codegen script automatically runs against the non-iframed
version of storybook, so while you can record interactions and use the resulting
script, you will likely need to adapt it for running inside the iframed version
of the page in the actual test.
