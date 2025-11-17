# Playwright tests

## Visual regression and end-to-end tests

We run the Playwright test suite on each PR to test that the front end works
correctly and there are no visual regressions.

The **end-to-end** tests make sure that functionality works as expected and are
located in `test/playwright/e2e`. They test, for instance, that we can open the
filters by clicking on the Filters button in the header, or select the filters
and execute the relevant search by clicking on the filter checkboxes.

There are also **visual regression** tests that make sure that the pages display
correct components, and components are rendered correctly. The components can be
tested in isolation to make sure that the states are correctly rendered. For
more on which states should be tested, see
[`Testing guidelines.md`](./testing_guidelines.md). These tests should use
Storybook to render the component in isolation, and be placed in
`frontend/test/storybook/visual-regression`.

The component tests that test that the component state is correctly rendered
based on the page interaction should be placed in
`frontend/test/visual-regression/components`. For example, the header elements
are tested this way because their appearance depends on the page scroll
position.

## Dockerization

Our Playwright test suite runs inside a docker container in order to prevent
cross-platform browser differences from creating flaky test behavior. We run
both end-to-end and visual-regression tests in the same container to save from
having to run the Nuxt production build twice.

Having Docker and Compose V2 is a pre-requisite to running the Playwright tests
locally. Please follow
[the relevant instructions for your operating system for how to install docker and docker-compose](https://docs.docker.com/get-docker/).
If you're on Windows 10 Home Edition, please note that you'll need to
[install and run docker inside WSL2](https://www.freecodecamp.org/news/how-to-run-docker-on-windows-10-home-edition/).
We strongly recommend (and only plan to support) Windows users run everything
inside of WSL.

If it's not possible for you to run docker locally, don't fret! Our CI will run
it on every pull request and another contributor who is able to run the tests
locally can help you develop new or update existing tests for your changes.

The Playwright docker container runs everything needed for the end-to-end and
visual-regression tests, including the Nuxt server and a
[Talkback proxy](https://github.com/ijpiantanida/talkback) for the API. It will
also generate and match against the existing visual-regression snapshots in the
codebase.

## Running the tests

To run the end-to-end tests, after having installed docker, run the following:

```bash
just frontend/run test:playwright
```

You may pass arguments to playwright directly, for example `-u` to update
snapshots or a filter.

```bash
just frontend/run test:playwright visual-regression -u
```

The above will run only test files with `visual-regression` in the path and will
update any snapshot tests due to the `-u` flag.

## Visual Regression tests

When writing visual regression tests, it is good practice to write tests for
each relevant breakpoint. There is a series of helpers in
[`frontend/test/utils/breakpoints.ts`](https://github.com/WordPress/openverse/blob/main/frontend/test/playwright/utils/breakpoints.ts)
for this. The most common usage for this module is to run a test or set of tests
for every breakpoint our app knows about or a subset of them. Occasionally you
will need to separate tests by breakpoint or by range for which there are also
helpers.

Each of the following methods expects a describe block callback function
accepting some useful helpers.

- `breakpoints.describeEvery`: Generates a describe block for every breakpoint
  our app is concerned with.
- `breakpoints.describeEachDesktop`: Generates a describe block for every
  breakpoint that roughly correlates with desktop and tablet width devices.
- `breakpoints.describeEachMobile`: Generates a describe block for every
  breakpoint that roughly correlates with smartphone sized mobile devices.
- `breakpoints.describeEachBreakpoint`: Accepts a list of breakpoints to
  generate describe blocks for, with similar syntax to `jest`'s `test.each`
  helper. Used like
  `breakpoints.describeEachBreakpoint(['xs', '2xl'])(<block>)`. `describeEvery`
  and the two `describeEach*` methods are aliases for pre-configured
  `describeEachBreakpoint`. It is unlikely that you will need to use this helper
  directly.

Additionally, there are describe blocks for individual breakpoints, each
following the pattern `` `describe${Capitalize<Breakpoint>}` ``, for example
`breakpoints.describeXs`.

The describe blocks are passed the following helpers:

- `breakpoint`: The name of the breakpoint for the current describe block.
- `getConfigValues`: Returns useful configuration values if running a snapshot
  test manually.
- `expectSnapshot`: A function accepting an identifier and a screenshot-able
  object. This will generate the screenshot and match it against a snapshot
  matching the name passed. Remember to `await` this function or else the
  `expect` will not be fired within the context of the test (you'll get a nasty
  error in this case).

Optionally, you may pass a configuration object as the first argument to the
`breakpoints.describe*` functions. If you do this, then the describe block is
the second argument.

The configuration object currently supports the following options:

- `uaMocking`: This `boolean` option defaults to `true`. When enabled, it will
  use a mock mobile browser user agent string for narrow viewports. Setting it
  to `false` for viewport widths above `md` (inclusive) is a no-op.

Please see the
[`homepage.spec.ts` visual-regression tests](https://github.com/WordPress/openverse/blob/main/frontend/test/playwright/visual-regression/pages/homepage.spec.ts)
as an example of how to use these helpers.

### What to test for visual regression

Visual regression tests can match entire pages or on individual elements in
specific states. They're useful, for example, to test the various focus, hover,
and active states of interactive elements. Use
[`page.locator`](https://playwright.dev/docs/api/class-page#page-locator) to
select specific elements to pass to `expectSnapshot`.

## API proxy

The Playwright test container also runs an API proxy using
[Talkback](https://github.com/ijpiantanida/talkback) to prevent network requests
from hitting the live API during end-to-end and visual-regression tests. This
significantly speeds up the tests and makes the data being tested against
consistent across test runs and eliminates variations that the API may include
after data refreshes happen.

The configuration for the Talkback proxy is in the
[`proxy.js`](https://github.com/WordPress/openverse/blob/main/frontend/test/proxy.js)
module and is run using `pnpm talkback`. It is rare and unlikely that you will
need to run it directly as running it is handled by the Playwright `webServer`
configuration.

If you've added new tests or updated existing ones, you may get errors about API
responses not being found. To remedy this, you'll need to update the tapes:

```bash
just frontend/run test:playwright:update-tapes
```

If for some reason you find yourself needing to completely recreate the tapes,
you may do so using the `test:playwright:recreate-tapes` script. Please use this
sparingly as it creates massive diffs in PRs (tens of thousands of lines across
over literally hundreds of JSON files). Note that you may be rate-limited by the
upstream production API if you do this. There is no official workaround for this
at the moment.

## Debugging

Additional debugging may be accomplished in two ways. You may inspect the trace
output of failed tests by finding the `trace.zip` for the relevant test in the
`test-results` folder. Traces are only saved for failed tests. You can use the
[Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer) to inspect
these (or open the zip yourself and poke around the files on your own).

For Playwright tests failing in CI, a GitHub comment will appear with a link to
download an artifact of the `test-results` folder.

Visual regression tests that fail to match the existing snapshots will also have
`expected`, `actual` and `diff` files generated that are helpful for
understanding why intermittent failures are happening. These are generated
automatically by Playwright and will be placed in the `test-results` folder
under the fully qualified name of the test that failed (with every parent
describe block included).

Additionally, you can run the tests in debug mode. This will run the tests with
a headed browser as opposed to a headless (invisible) one and allow you to watch
the test happen in real time. It's not possible for a headed browser to run
inside the docker container, however, so be aware that when debugging the
environment will be slightly different. For example, if you're on any OS other
than Linux, the browser you're running will have small differences in how it
renders the page compared to the docker container.

To run the debug tests:

```bash
just frontend/run test:playwright:debug
```

Note that this still runs the talkback proxy and the Nuxt server for you. If
you'd like to avoid this, simply run the Nuxt server before you run the
`test:playwright:debug` script and Playwright will automatically prefer your
previously running Nuxt server.

<aside>
For some reason the following two tests are consistently flaky when updating tapes but appear to be stable when running the e2e tapes with pre-existing tapes.

```
search-types.spec.js:102:3 › Can open All content page client-side
search-types.spec.js:102:3 › Can open Images page client-side
```

Don't be alarmed if you notice this.

</aside>

## Generating new tests

When writing end-to-end tests, it can be helpful to use Playwright
[codegen](https://playwright.dev/docs/cli#generate-code) to generate the tests
by performing actions in the browser:

```bash
just frontend/run test:playwright:gen
```

This will open the app in a new browser window, and record any actions you take
in a format that can be used in end-to-end tests.

Note that this does _not_ run the server for you; you must run the Nuxt server
using `pnpm start` or `pnpm dev` separately before running the codegen script.

To generate tests for a non-default breakpoint, set the viewport size using the
`--viewport-size` flag. For example, to test the `xs` breakpoint, run:

```bash
just frontend/run test:playwright:gen --viewport-size=340,600"
```
