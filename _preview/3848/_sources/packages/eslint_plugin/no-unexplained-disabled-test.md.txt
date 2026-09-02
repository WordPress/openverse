# `no-unexplained-disabled-test`

Ensures that disabled tests have an issue comment with a GitHub link preceding
them.

Enforces the following conventions:

- Checks for disabled tests marked with functions skipped functions such as
  `test.skip`, `test.todo`, `it.skip`, `it.each.skip`, `describe.skip`, etc.,
- Verifies that each disabled test has an issue comment with a valid GitHub link
  preceding it

## Rule Details

Examples of **incorrect** code using this rule:

````{admonition} Incorrect
:class: error

```ts
test.skip('invalid skipped test', () => {
  // Some comments without issue link
});

it.skip('another invalid skipped test', () => {
  // Missing issue comment
});

describe.skip('my skipped suite', () => {
  // ... tests will be skipped
});
```
````

Examples of **correct** code using this rule:

````{admonition} Correct
:class: tip

```ts
// https://github.com/your-org/your-repo/issues/123
test.skip('valid skipped test', () => {
  /* implementation */
});

/**
 * A skipped test with a preceding multi-line comment:
 * https://github.com/your-org/your-repo/issues/456
 */
it.skip('skipped test with comments', () => {
  /* implementation */
});
```
````
