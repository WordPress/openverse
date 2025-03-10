# Test

## Docker

1. Before running the tests, make sure to initialise the system with data.

   ```bash
   just init
   ```

   This step is a part of the {doc}`"Quickstart" <./quickstart>` process.

2. Run the tests in an interactive TTY connected to a `web` container.
   ```bash
   just api/test
   ```

## Flaky tests

Openverse treats flaky tests as a critical issue. The rationale behind this is
founded on the assumption that the tests in our test suites are individually
necessary for verifying the detailed correctness of our applications. Given that
assumption, if a test is flaky, then it cannot be relied on to verify the
correctness of the application, either because it sometimes reports that the
application is not working when, in fact, it is; or, perhaps even worse, the
test could report that the application is working when in fact is it not.

Therefore, if a test is identified as flaky, we follow the process below to
triage the issue:

1. Create an issue with critical priority documenting the flaky test. Link to
   failed CI runs or copy/paste relevant logs and output if they exist. The goal
   of this issue is not to document the solution, merely to document the fact of
   the flakiness and to prioritise someone picking the issue up much sooner to
   fix it. Of course, if you have additional details or ideas, proactively share
   those in the issue description or discussion.
1. Open a PR that skips the flaky test with a link to the issue as a comment or
   in the explanatory note of the skip annotation. This PR should also be marked
   with critical priority.

The critical issue will be prioritised and assigned during the following week's
prioritisation or community meeting, though anyone is free to work on flaky test
resolution if they are able to.

A
[GitHub Discussion about flaky tests](https://github.com/WordPress/openverse/discussions/1824)
is the original impetus for the development of this process. As will all
Openverse processes, it should be iterated on and improved over time.

### Identifying a "flaky test"

A test is "flaky" if it passes or fails when we do not expect it to do so. The
most common situation is for a test to fail when we did not expect it to fail.
Be wary of false-positives when identifying flaky tests. Just because a given
change does not look like it would cause a certain test to fail, double check
that the test isn't correctly failing due to the changes. Sometimes tests do not
have obvious relationships to every part of the code-base that affects them,
especially integration or end-to-end tests.

Identifying tests that pass when they shouldn't is _much_ harder but arguably an
even more serious problem than false-negatives. It's one thing for a test to
annoyingly fail when it shouldn't. It's an entirely different thing for a test
to _pass_ and give us false-confidence that our applications are working as
expected. False-negatives do not usually have a downstream effect on Openverse
API or frontend consumers, for example. False-positives, on the other hand,
usually mean that issues are caught only once they're in production and
affecting users.

### Test skip utilities

Openverse uses pytest, Playwright, and jest for various different types of
testing. Links to each library's test-skipping approach are below:

- pytest:
  <https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest-skip>
- Playwright:
  - `test.skip`: <https://playwright.dev/docs/api/class-test#test-skip-1>
  - `test.describe.skip`:
    <https://playwright.dev/docs/api/class-test#test-describe-skip>
- jest:
  - `test.skip`/`it.skip`: <https://jestjs.io/docs/api#testskipname-fn>
  - `describe.skip`: <https://jestjs.io/docs/api#describeskipname-fn>

```{note}
Jest and Playwright's `describe.skip` utilities should be used lightly and
only if either the entire describe block is flaky or if the tests inside the
block are interdependent and skipping an individual test will cause subsequent
tests to incorrectly fail.
```
