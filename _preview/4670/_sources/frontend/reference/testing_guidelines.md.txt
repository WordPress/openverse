# Testing Guidelines

This document describes general guidelines you should follow when testing the
/frontend pull requests. It is not exhaustive but should be the starting point
that you adapt for each PR. You may also use your best judgement and skip things
that are unrelated to a specific PR. However, please be careful when doing this
as accessibility bugs _especially_ are easy to slip through the cracks when we
aren't doing our due diligence and testing changes thoroughly.

## Running the application

Please follow the instructions in the README for how to set up and run the
application locally. If you want to just generally test the application in its
current state (i.e., what exists on `main` as opposed to what has actually been
deployed to production) you can find the staging deployment here:

https://staging.openverse.org

Staging is redeployed every time we merge to the `main` branch, so if you're
looking to test the latest version of the app without going through the local
set up, that's the easiest way to go.

Once you have the application running, you can visit it in your browser at
http://localhost:8443.

You can also access it from other devices in your same network (like a mobile
phone) for additional testing. See the
[finding your local IP address](/frontend/reference/miscellaneous.md#finding-your-local-ip-address)
section of the README for how to identify the local IP address Nuxt is served
on. Once you have identified your local IP address, you can access the website
running on your computer by visiting `https://<local IP>:8443` replacing
`<local IP>` (including the brackets) with the value you found using the
instructions above in your mobile device's browser.

Testing from multiple different devices as often as possible is a great way to
contribute to Openverse's frontend development.

### API Authentication

By default, the application will run using the production API without
authentication. This means your local frontend server may be subject to the
unauthenticated rate limiting, depending on your testing behavior. There are two
ways to solve this:

1. You can change your local Nuxt server to point to a local API server that
   does not have throttling enabled
2. You can introduce the environment variables necessary for authenticating with
   an API

For the first, [run the Openverse API locally](/api/guides/quickstart.md). Then
create a `.env` file by copying the `.env.template` file and update it with the
following:

```shell
API_URL="http://localhost:8000/"
```

Be sure to remove the leading `#` to uncomment the variable from the copied
template.

The run the dev server as usual:

```shell
pnpm dev
```

For the second, you'll need to follow
[the instructions to set up an OAuth application](https://api.openverse.org/v1/#section/Register-and-Authenticate)
and then fill in the `API_CLIENT_ID` and `API_CLIENT_SECRET` in the `.env` file
copied from `.env.template`. Be sure to remove the leading `#` to uncomment
these variables from the copied template.

```shell
API_CLIENT_ID=""
API_CLIENT_SECRET=""
```

Then run the API as usual using `ov just api/up` & `ov just api/init`. Nuxt
automatically loads `.env` files into the environment. With these variables in
the environment, all requests made by your server will be made using an access
token retrieved by the `~/plugins/api-token.server.ts` plugin.

Once the `.env` file is set up, you may run the development build the typical
way:

```shell
ov just frontend/run dev
```

## Browsers

In addition to testing on multiple devices, we also strive to test on almost all
widely used browsers excluding Internet Explorer. Please be ready to regularly
test your work and the work of others in Firefox, Chrome, and Safari on a
desktop computer. On mobile devices, Mobile Safari on iOS, Firefox for Android
and Mobile Chrome on iOS are all important targets for testing as well. A
significant amount of web traffic is mobile these days.

## Accessibility

### Prerequisite reading

Please review the
[WordPress Accessibility Handbook](https://make.wordpress.org/accessibility/handbook/).

The [WAI-ARIA](https://www.w3.org/TR/wai-aria/) spec. This document describes,
in detail, all of the documented types of interactions that happen on most
websites and the accessibility properties of them. Many of them also include
examples.

Gutenberg also has an excellent
[Accessibility Testing Guide](https://github.com/WordPress/gutenberg/blob/5413ddbced8cbe0f0f10eb7739dbc34a7e56adee/docs/contributors/accessibility-testing.md)
with specific instructions for setting up screen readers for testing with.

### General recommendations

Practice using keyboard navigation when you run the app locally generally. This
will reveal to you some of the initial hurdles that the app currently presents
to users who rely on assistive technology. Note that keyboard accessibility is
part of the bare-minimum in accessibility for a website along with accessible
color contrasts.

If you are a regular contributor, at least once a week, attempt to use the site
using a screen reader like VoiceOver on macOS, NVDA on Windows, or Orca on
Linux. If you do not regularly rely on a screen reader for navigating the web,
it can also stretch your comfort level a lot by closing your eyes or turning off
your monitor while navigating using the screen reader. Keep in mind that many
people who rely on screen readers to navigate the web do not have any of the
visual context that a sighted user is using to interpret a website. This
especially applies to directionality and the _broad_ context of a page. Screen
readers can't "see" what's at the "end" of the page unless the user navigates
all the way there. Sighted users have a huge privilege in being able to take in
the broader context of a website almost immediately through visual information.

## Specific things to test for

### Focus styles

Buttons, form fields, and other interactive elements should all have visible and
high contrast focus styles applied. Please note that hover styles are _not_ the
same as focus styles and are often distinct. Note also that hover styles and
focus styles may not always be applied at the same time. It is best to test the
following scenarios:

1. Hover over the element, unfocused
2. Focus the element using the keyboard, no mouse hover
3. Focus the element using the keyboard and also hover over it with the mouse

That will exhaust 95% of the interactions that visible focus styles need to
cover.

### Interactiveness

Buttons should be able to be activated using mouse click, <kbd>Enter</kbd> and
<kbd>Space</kbd> keys. Links should be able to be activated using a mouse click
and <kbd>Enter</kbd> but not <kbd>Space</kbd>.

Arrow keys are common methods for navigating distinct UI elements, especially
composite groups like field sets, radio groups, menus, and other
[composite elements](https://www.w3.org/TR/wai-aria-1.1/#composite). Please test
these interactions and compare them against the WAI-ARIA examples for the same
UI components.

### Screen reader intelligibility

When testing a new piece of UI, please test it thoroughly with a screen reader
paying close attention to what the screen reader is saying, in particular how it
is describing parts of the page.

Buttons, for example, should have appropriate labels. If the visible text of the
button relies on some wider visual context to be intelligible, ensure that it
has an appropriate `aria-label` that a screen reader can use to give more
information about the button.

### Server vs client side render

The Openverse frontend is a Nuxt SSR application. This means the initial Vue
page rendering when you make a request is processed by a server and then
delivered to you to be "hydrated" with the current state of the page. The
implication of this is that there are two ways for _every single page_ to be
rendered, and we should test with that in mind. Please make sure that you are
testing client side navigation as well as SSR. To test SSR for a page, simply
reload the page: it will be rendered in SSR and then delivered to your browser.
To test client side rendering for a page, navigate to that page from another
page without reloading the page in between. For example, to test the search
route client side, you can execute a search from the homepage and it will
redirect you client-side to the search page.

### Conclusion

Please note that these are non-expert and non-exhaustive recommendations. Spend
time reading the [WAI-ARIA spec](https://www.w3.org/TR/wai-aria/) and other web
accessibility materials. Even just knowing about specific roles and interactions
that exist and are meant to be developed in consistent ways is a good first step
to learning what to look out for when testing.

## Automated tests

Openverse uses
[Vue Testing Library](https://testing-library.com/docs/vue-testing-library/intro/)
for unit testing with [Jest](https://jestjs.io/docs/getting-started), and
[Playwright](https://playwright.dev) for end-to-end and visual-regression
testing.

There are also legacy unit tests written in
[Vue Test Utils](https://vue-test-utils.vuejs.org/) but those are slated to be
re-written using testing library.

### Playwright tests

<!-- ## Visual regression and end-to-end tests -->

We run the Playwright test suite on each PR to test that the front end works
correctly and there are no visual regressions.

The **end-to-end** tests make sure that functionality works as expected and are
located in `test/playwright/e2e`. They test, for instance, that we can open the
filters by clicking on the Filters button in the header, or select the filters
and execute the relevant search by clicking on the filter checkboxes.

The component tests that test that the component state is correctly rendered
based on the page interaction should be placed in
`frontend/test/visual-regression/components`. For example, the header elements
are tested this way because their appearance depends on the page scroll
position.

### Storybook tests

There are also **visual regression** tests that make sure that the pages display
correct components, and that the components are rendered correctly. The
components can be tested in isolation to make sure that the states are correctly
rendered and so that we don't have to duplicate things like focus state testing
into our application-level tests. These tests should use Storybook to render the
component in isolation, and be placed in
`frontend/test/storybook/visual-regression`.

You will find the functional component tests in `/test/storybook/functional`,
and visual regression tests with snapshots in
`/test/storybook/visual-regression`

### Visual Regression tests

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

### Writing tests

#### Playwright

When writing end-to-end tests, it can be helpful to use Playwright
[codegen](https://playwright.dev/docs/codegen#running-codegen) to generate the
tests by performing actions in the browser:

```bash
ov just frontend/run test:playwright:gen
```

This will open the app in a new browser window, and record any actions you take
in a format that can be used in end-to-end tests.

Note that this does _not_ run the server for you; you must run the Nuxt server
using `pnpm start` or `pnpm dev` separately before running the codegen script.

To generate tests for a non-default breakpoint, set the viewport size using the
`--viewport-size` flag. For example, to test the `xs` breakpoint, run:

```bash
ov just frontend/run test:playwright:gen --viewport-size=340,600"
```

#### Storybook

It is preferable to write tests using the iframed version of the component to
avoid Storybook UI updates from effective snapshots. To access this, take the
`path` query parameter for any story and apply it to the `/iframe.html` route.
See
[`v-checkbox.spec.ts` for an example](https://github.com/WordPress/openverse/blob/main/frontend/test/storybook/visual-regression/v-checkbox.spec.ts)

You can use Playwright's
[codegen](https://playwright.dev/docs/codegen#running-codegen) tool to generate
tests. For this you will need to run Storybook locally on your own using
`ov just frontend/run storybook`. Then run:

```bash
ov just frontend/run test:storybook:gen
```

Please note that the codegen script automatically runs against the non-iframed
version of storybook, so while you can record interactions and use the resulting
script, you will likely need to adapt it for running inside the iframed version
of the page in the actual test.

### Debugging

Additional debugging may be accomplished in two ways. You may inspect the trace
output of failed tests by finding the `trace.zip` for the relevant test in the
`test-results` folder. Traces are only saved for failed tests. You can use the
[Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer) to inspect
these (or open the zip yourself and poke around the files on your own).

Playwright tests in CI are run with `-u` option by default, this means that
snapshots will automatically be updated for modified parts of the UI if
Playwright detects that. See
[Updating snapshots](/frontend/guides/test.md#updating-snapshots) for more
reading about this.

When this happens, a GitHub comment will appear with a link to download zipped
artifacts named in the form `*_snapshot_diff.zip`. Download and save this to the
repository root. Once downloaded, decompress and apply them to your working
branch by running:

`ov unzip -p *_snapshot_diff.zip | git apply`

The above command basically uses the `unzip` tool to unpack the contents of the
downloaded archive file named `*_snapshot_diff.zip`, the `-p` option prevents it
from actually creating any extracted file but rather prints the contents to the
standard output which is then piped to `git apply`.

```{note}
Remember to replace `*_snapshot_diff.zip` with the actual downloaded filename.

Keep in mind that you'd need to delete the downloaded file
(`*_snapshot_diff.zip`) from the repository after successfully applying
the changes to avoid committing them.

```

After successfully applying the patch, stage, commit and push the latest changes
to your branch upstream and you should most likely have Playwright CI tests
pass.

Visual regression tests that fail to match the existing snapshots will also have
`expected`, `actual` and `diff` files generated that are helpful for
understanding why intermittent failures are happening. These are generated
automatically by Playwright and will be placed in the `test-results` folder
under the fully qualified name of the test that failed (with every parent
describe block included). This is also available for download in the Artifacts
section after every failed Playwright test in the CI.

Additionally, you can run the tests in debug mode. This will run the tests with
a headed browser as opposed to a headless (invisible) one and allow you to watch
the test happen in real time. It's not possible for a headed browser to run
inside the docker container, however, so be aware that when debugging the
environment will be slightly different. For example, if you're on any OS other
than Linux, the browser you're running will have small differences in how it
renders the page compared to the docker container.

To run the debug tests:

```bash
ov just frontend/run test:playwright:debug
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

### Dockerization

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

### API proxy

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
ov just frontend/run test:playwright:update-tapes
```

If for some reason you find yourself needing to completely recreate the tapes,
you may do so using the `test:playwright:recreate-tapes` script. Please use this
sparingly as it creates massive diffs in PRs (tens of thousands of lines across
over literally hundreds of JSON files). Note that you may be rate-limited by the
upstream production API if you do this. There is no official workaround for this
at the moment.
