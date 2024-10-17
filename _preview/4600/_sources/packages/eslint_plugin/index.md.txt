# `@openverse/eslint-plugin`

A collection of custom ESLint rules and rule configurations used by Openverse.
Please consult each rule's page for documentation regarding the rule.

```{toctree}
:glob:
:titlesonly:

*
```

## Development

All ESLint plugin rules and configuration must be written in TypeScript.

All rules must have unit tests added using `RuleTester` from the
`@typescript-eslint/rule-tester` package. Use the `@typescript-eslint/parser` as
the `parser` option.

All rules are required to have a documentation page in this documentation
section. Rule documentation should follow the typical ESLint rule documentation,
including samples of valid and invalid code with options clearly documented. See
existing rule documentation for examples.
