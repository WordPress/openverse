# Implementation Plan - 2022-02-17

A proposal to integrate visual regression testing into the Openverse frontend's
automated testing suite.

## Reviewers

- [x] @obulat
- [x] @AetherUnbound

## Milestone

https://github.com/WordPress/openverse-frontend/milestone/7

## Exploratory code

https://github.com/WordPress/openverse-frontend/pull/899

## Background

### What is "visual regression testing"?

Visual regression testing is a testing strategy that diffs two screenshots
reports a failure if there are significant differences between the two.

Playwright is capable of generating and diffing screenshots of the running
application via the
[screenshot function](https://playwright.dev/docs/screenshots) available on the
`Page` and `Locator` objects. These can be used with `toMatchSnapshot` like so:

```ts
expect(await page.screenshot()).toMatchSnapshot({
  name: "fullpage",
})
```

Playwright uses the popular [pixelmatch](https://github.com/mapbox/pixelmatch)
library to diff the screenshots. Example diffs
[can be found here](https://github.com/mapbox/pixelmatch#example-output).
Playwright on its own does not appear capable of outputting the visual-diff
image. An alternative to this is covered below.

### Rationale for this style of testing

A lot of the recent regressions that we've experienced on the frontend _on
critical paths_ have been visual style regressions. It's difficult, but not
impossible, to write "sensible" unit tests against the applied styles. Testing
Library offers the
[`toHaveStyle`](https://github.com/testing-library/jest-dom#tohavestyle) matcher
and we _could_ start utilizing this more, but it would require tedious manual
changes to tests that _most of the time_ would just be 1-1 confirmations of the
applied Tailwind classes. It also doesn't necessarily test components in
composition very well and it would be tedious to write individual specific style
tests for each of the scenarios any given widespread component is used in
(`VButton`, for example, is used everywhere).

Visual regression testing could be a way of accomplishing more robust tests
without the tedious practice of hand-writing tests for specific styles.

### Existing tooling

We already utilize Playwright for our end-to-end tests. Provided we wrote the
requisite tests to generate the screenshots, we could stop here and already have
visual regression testing.

However, we also need a way of easily reviewing the diffed images. Luckily,
[GitHub already has this functionality built into it's PR diff previews](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#viewing-differences).
This means when an existing screenshot is replaced we'd be able to review and
approve this change as a normal part of our PR review process, just like we
review code.

### Alternative/additional tooling

Everything in the previous section is basically the "bare minimum" of what we'd
need to start utilizing visual regression testing. We could stop there and
already be able to take advantage of this technology. However, there are
additionally a whole world of visual regression testing tools. In this section I
cover one popular external diff reviewing tool (which I ultimately recommend
against, for now) and an enhanced image snapshot matcher.

#### Percy

[Percy](https://percy.io/) seems to be far and away the most powerful tool for
reviewing image diffs. It is owned by BrowserStack. While BrowserStack has a
generous open source sponsorship (that we should definitely eventually utilize
to run e2e tests and even potentially generate snapshots on real mobile
devices), they do not appear to extend this offering to Percy[^1].

Percy also requires you to specifically upload the files through a GitHub action
which would require managing additional secrets. It would also restrict
reviewers to those with access to Percy which would unnecessarily exclude casual
contributors.

Percy definitely looks very cool and I would recommend creating a BrowserStack
account and checking out the Percy demo project. It's fun to poke around in and
the UI mostly works very nicely.

However, if I'm being honest, when taking into account the fact that GitHub
already has image diffing built into the PR review process, Percy seems like an
unnecessary additional complication to the baseline of visual regression
testing. Maybe it's something that we would come to realize the value of down
the line, but it does not seem to me to be a requirement for the initial phase
of visual regression testing.

#### Alternative image snapshot libraries

Playwrights's built in image snapshot-diffing capability works fine for the most
part. In fact, it basically does everything you need short of one very useful
feature: it throws away the actual generated diff.

[Amex's `jest-image-snapshot`](https://github.com/americanexpress/jest-image-snapshot)
fixes this. In addition to failing when snapshots do not match, it will also
write the diff image that includes the "hot spots" where the visual differences
exist. It also automatically generates the snapshot name, which Playwright's
matcher doesn't seem to be capable of (this is usually a standard feature of
Jest snapshot matchers otherwise).

`jest-image-snapshot` is also significantly more configurable than Playwright's
matcher. Playwright's matcher has a single option, `threshold` which it passes
directly to `pixelmatch`. Amex's library has a
[ton of potentially useful options for configuring snapshots on an individual basis or project wide](https://github.com/americanexpress/jest-image-snapshot#%EF%B8%8F-api)
and also still uses `pixelmatch` in the background anyway.

**Important caveat to this section!**

I ended up trying out `jest-image-snapshot` in
https://github.com/WordPress/openverse-frontend/pull/899 but running the matcher
fails on some error about `_counters` being undefined. It looks like Playwright,
while it uses the jest `expect` library, does not support the same matcher
context as Jest proper does. To use `jest-image-snapshot` we might have to
switch to `jest-playwright` which would be less than ideal as it's
[recommended against by the Playwright project](https://playwright.dev/docs/test-runners#jest--jasmine)
(though for what reason exactly I'm really not sure).

We can still _try_ to find a workaround for this, but if it ends up being too
much trouble I'd say just leave it out of the final roadmap for this feature and
we can use the built-in Playwright tool. Playwright will output the before and
after images for failed snapshot comparisons into a `test-results` folder at the
top level of the project, so I figure the worst case scenario is that we could
write a little script to walk through that directory and run `pixelmatch` on
them to get the diff image.

## Repository size considerations

Storing many images in a Git repository can be problematic. Between using more
of our contributor's bandwidth in uploading and downloading images to just
generally butting up against the limit of GitHub's repository size limit.

The repository size limit I don't think we'll ever need to worry about. GitHub
has a
[repository size limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github#repository-size-limits)
of 100GB. Playwright screenshots are small (in the kilobytes) so it would take a
very long time and tons and tons of screenshots to start getting close to the
repo size limit.

However, if we're not careful we could significantly increase the size of our
repository which would adversely effect contributors by eating their bandwidth
when pushing or pull contributions. There are some strategies we could use if
this becomes a problem. For example we could use git's `clean` and `smudge`
features to losslessly compress and decompress the snapshot images
automatically, though I'm not sure how well that would work[^2]. Before we
invested too much in that, however, we'd want to ensure that more typical,
though lossy,
[git repository size reduction](https://stackoverflow.com/questions/2116778/reduce-git-repository-size#2116892)
isn't a better option.

Ultimately I think the best option would be to regularly (once a day) run a
scheduled maintenance task to remove any historical snapshots older than a month
that are not currently used by the main branch. That would mean we would always
have a _reasonable_ historical view of snapshots that change frequently and I
frankly doubt snapshot history extending more than a month back would be very
useful anyway.

## Cross platform rendering

Browsers will sometimes render minute differences between platforms, even with
the exact same webpage. This means that contributors running Linux might
generate different screenshots from those running macOS and again from those
running Windows, even if they're all using the same browser and version.

To avoid this, other visual regression testing libraries like BackstopJS support
running tests inside a docker container and using the browser inside the
container. We can do the same with Playwright (it's just not as easy).

I was about to figure out "a way" of doing it. Here's what I came up with:

1. Create a `./bin/visual-regression.js` file with the following:

```js
/**
 * Run this as a node script so that we can retrieve the `process.cwd`
 * which isn't possible to evaluate cross-platform inside an package.json script
 *
 * We can also automatically sync the local playwright version
 * with the docker image version. This ensures that the browser
 * versions expected by the `playwright` binary installed locally
 * matches the versions pre-installed in the container.
 */
const { spawnSync } = require("child_process")
const fs = require("fs")
const path = require("path")
const yaml = require("yaml")

const pnpmLock = yaml.parse(
  String(fs.readFileSync(path.resolve(process.cwd(), "pnpm-lock.yaml")))
)

const playwrightVersion = pnpmLock.devDependencies["@playwright/test"]

const args = [
  "run",
  "--rm",
  "-it",
  "--mount",
  `type=bind,source=${process.cwd()},target=/src`,
  "--add-host=host.docker.internal:host-gateway", // This is necessary to make `host.docker.internal` work on Linux. Does it break the command for other OSs?
  `mcr.microsoft.com/playwright:v${playwrightVersion}-focal`,
  "/src/bin/visual-regression.sh",
]

if (process.argv.includes("-u")) {
  args.push("-u")
}

spawnSync("docker", args, {
  stdio: "inherit",
})
```

2. Create a `./bin/visual-regression.sh` file containing the following (don't
   forget to `chmod +x` it):

```sh
#!/bin/bash
# This script is meant to run inside the playwright docker container, hence the assumed `/src` directory
cd /src

# Use npm to avoid having to install pnpm inside the container, it doesn't matter in this case
npm run test:visual-regression:local -- $1
```

3. Add two new package.json scripts:

```json
"test:visual-regression": "node ./bin/visual-regression.js",
"test:visual-regression:local": "playwright test -c ./test/visual-regression"
```

All of this together should successfully allow us to run the snapshot tests
inside a docker container.

For local debugging purposes, `pnpm test:visual-regression:local --debug` can be
used to run the snapshot tests headed in a browser on the host OS. This is
useful for debugging the playwright scripts before they actually take a
screenshot. Just keep in mind that the final screenshots submitting in a PR need
to come from the docker container.

## Additional cross-platform considerations

Some versions of Windows
[do not allow installing Docker](https://www.freecodecamp.org/news/how-to-run-docker-on-windows-10-home-edition/);
additionally, Docker may not be available on someone's machine for licensing
reasons and alternatives like containerd and Podman are not yet wide-spread
enough to be reliably available on contributor machines.

For that reason, it'd be good to consider ways for making sure snapshots are
able to be updated without Docker being available locally (props to @obulat for
mentioning this potential roadblock for contributors). I'd like to propose a new
GitHub workflow that runs if the `ci:visual-regression` script fails.

The workflow would create a new branch based on the PR with the changes using
the pattern `<pr branch name>__vr-snapshot-update`, run
`ci:visual-regression:update` (we'd need a new script for this to pass the `--u`
flag to our script specifically instead of to the e2e `run-server-and-test`
utility), commit the changes in the new branch and open a PR targeting the
parent PR with the changes.

This PR could then be merged directly into the parent PR after the snapshot
changes are reviewed.

Additionally, subsequent pushes to the parent PR that include changes to the
snapshots would re-use the same branch name and just force push; there'd only
ever be a single commit in the companion branch this way and we wouldn't have to
worry about a muddied commit history. Ideally this will simplify the
implementation of the workflow rather than complicate it.

Likewise, if we end up needing to run `pixelmatch` directly to generate the diff
output, it'd be nice if we could just add those diff outputs as a comment in the
parent PR whenever snapshot images are updated.

## Test variants

Most tests should be written against two parameters: language direction and
breakpoint.

For language direction, the best way to do this is to just test in the default
locale which is LTR and to test in Arabic (`ar`) which is RTL.

For breakpoints, it will be tedious to have to add the iteration for each test
case, so I've written a utility that we can use to make this easier. This
utility can also be used for our regular end-to-end tests:

```ts
import { test, PlaywrightTestArgs, TestInfo } from "@playwright/test"

import { Breakpoints, SCREEN_SIZES } from "../../../src/constants/screens"

export const testEachBreakpoint = (
  title: string,
  testCb: (
    breakpoint: Breakpoints,
    args: PlaywrightTestArgs,
    testInfo: TestInfo
  ) => Promise<void>
) => {
  SCREEN_SIZES.forEach((screenWidth, breakpoint) => {
    test.describe(
      `screen at breakpoint ${breakpoint} with width ${screenWidth}`,
      () => {
        test(title, async ({ page, context, request }, testInfo) => {
          await page.setViewportSize({ width: screenWidth, height: 700 })
          await testCb(breakpoint, { page, context, request }, testInfo)
        })
      }
    )
  })
}
```

It's then used in the test like so:

```ts
test.describe("homepage snapshots", () => {
  // Repeat below for `rtl`
  test.describe("ltr", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/")
    })

    testEachBreakpoint("full page", async (breakpoint, { page }) => {
      await deleteImageCarousel(page)

      expect(await page.screenshot()).toMatchSnapshot({
        name: `index-ltr-${breakpoint}`,
      })
    })
  })
})
```

## Recommended tooling

- Continue using Playwright to manipulate the browser and use it's `screenshot`
  function to generate screenshots.
- _Try_ to use `jest-image-snapshot` to save and diff screenshots.
- Run snapshot tests inside a docker container to avoid cross-platform rendering
  differences.
- Write a GitHub action to be run
  [once daily using the `on.schedule` feature](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onschedule)
  to automatically remove snapshots from the repository history older than a
  month old.
- Use GitHub's PR review UI to review visual diffs of snapshots.
- Write Playwright scripts using TypeScript
  - Note: TypeScript linting and general infrastructure has already been set up
    in https://github.com/WordPress/openverse-frontend/issues/921 and
    https://github.com/WordPress/openverse-frontend/pull/917.

## Implementation plan

Once the final version of this RFC is approved, a milestone with issues for each
individual checkbox listed below will be created.

- [ ] Configure local visual regression testing:

  - Create a `playwright.config.ts` file in the new directory with the following
    code:

  ```ts
  // /test/visual-regression/playwright.config.ts
  import { PlaywrightTestConfig } from "@playwright/test"

  export default {
    testDir: ".",
    use: {
      baseURL: "http://localhost:8443",
    },
    timeout: 60 * 1000,
  } as PlaywrightTestConfig
  ```

  - Add the two `bin/visual-regression.{sh,js}` files described in the "Cross
    platform rendering" section above.
  - Add three new scripts to the root `package.json` (**Note: in light of
    https://github.com/WordPress/openverse-frontend/pull/881 these scripts will
    also need to be updated to use talkback to mock API calls during e2e!**):

  ```
  "test:visual-regression": "node ./bin/visual-regression.js",
  "test:visual-regression:local": "playwright test -c test/visual-regression",
  "ci:visual-regression": "start-server-and-test run-server http://localhost:8443 test:visual-regression"
  ```

  - Install and configure `jest-image-snapshot` and
    `@types/jest-image-snapshot`:
    - Note: It may be necessary to add additional TypeScript typings in the root
      level `typings` folder for TypeScript to know that `expect()` includes the
      `toMatchImageSnapshot` function. Follow the existing examples extending
      `@types/nuxt` to extend the `@playwright/test` library's `Matchers`
      interface.
    - Additional note: As mentioned in the section about `jest-image-snapshot`
      above it may not be possible to get this library to play nicely with
      Playwright's specific `expect.extend` context. I'd say time box trying to
      get this to work to an hour or so and then just move on to the next thing.
      There's an additional task at the end of this list for writing the
      `pixelmatch` diff generator script in case we need it.
    - **Extra important note:** This library might not work with Playwright, in
      which case we'll just leave this out; there's a contingency plan for this
      case below.
  - Write basic tests for the homepage; a full-page snapshot for `ltr` and `rtl`
    versions of the page using `testEachBreakpoint` should do just as a start
    and proof-of-concept.
    - Note: It will be necessary to remove the featured images from the page
      before taking the snapshot or the diff will fail 2/3 of the time due to
      them being different. The following code can be used to accomplish this:
    ```ts
    const deleteImageCarousel = async (page: Page) => {
      const element = await page.$('[data-testid="image-carousel"]')
      await element.evaluate((node) => node.remove())
      element.dispose()
    }
    ```
  - Create a `README.md` in the `visual-regression` directory with basic
    instructions for how to run and write visual regression tests. In particular
    mention our usage of `jest-image-snapshot` instead of the built in snapshot
    matcher.

- [ ] Complete https://github.com/WordPress/openverse-frontend/issues/890 if it
      isn't already done.
- [ ] Configure CI to run visual regression tests.
  - Write a new workflow to run the visual regression tests. You should be able
    to copy the existing e2e workflow and replace the call to `ci:e2e` to
    `ci:visual-regression`.
- [ ] Configure Storybook visual regression tests.
  - Copy the existing `visual-regression` folder's configuration and create a
    new test folder called `storybook-visual-regression`.
  - Create corresponding local and CI scripts in `package.json` to run these
    tests, using `storybook` instead of `run-server` and use the correct port
    for Storybook
  - Write basic state and variation tests for each button variant (or some other
    straight component with similar easy to configure props).
  - This will also establish a pattern for writing e2e tests against Storybook.
  - Copy the visual regression test CI and swap the appropriate scripts to run
    the Storybook ones instead.
    - If possible, create a shared action that can be re-used between all the
      Playwright based test workflows.
- [ ] Write a script to generate `pixelmatch` diffs from failed test results in
      the `test-results` folder created my Playwright.
  - **Contingent on `jest-image-snapshot` not being able to be used**
- [ ] Write a new GitHub workflow to generate supplemental PRs with updated
      snapshots whenever there are outdated snapshots.
- [ ] Write a new GitHub workflow to generate the snapshot diffs and upload them
      as a comment in the PR with snapshot changes.
- [ ] Create a scheduled GitHub action to clean the repository history of
      snapshot images older than a month in age outside of the `main` branch.
  - I tried searching for prior art here and there isn't much aside from how to
    completely remove a directory or file from history (usually because
    something illegal or secret was committed). I think `git filter-branch` is
    perfect for this though:
  ```bash
  git filter-branch --prune-empty --tree-filter './bin/clean_historical_snapshots.sh' HEAD
  ```
  But the devil's the details... The implementation of
  `clean_historical_snapshots.sh` will take some care and frankly there will
  need to be some stateful file hashes written to a temporary directory to be
  used by the script to skip current snapshots from deletion. We'll also want to
  establish a pattern for the snapshot directory names that can be easily
  followed for this purpose.
  - **Low priority, can be delayed up to a month or longer; really it can be
    delayed until we notice a problem with the repository size.**

<hr />

[^1]:
    I could be wrong about this. I tried searching around for it but couldn't
    find it and it was not included in the default set of allowances we got with
    out initial application as an OSS project.

[^2]:
    There's very little information about this online so I suspect it's a
    _non-problem_ for the most part.
