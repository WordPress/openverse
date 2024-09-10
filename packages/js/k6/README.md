# `@openverse/k6`

**This is an internal, non-distributable package**.

This package houses Openverse's k6 scripts.

[Refer to k6 documentation to learn more about the tool and its capabilities](https://grafana.com/docs/k6/latest/).

To run k6 scripts, use the just recipe:

```shell
ov run {namespace} {scenario} [EXTRA_ARGS]
```

For example, to run all frontend scenarios:

```shell
ov run frontend all
```

## Development tips and guidelines

- Code is written in TypeScript. k6's
  [`jslib` packages](https://grafana.com/docs/k6/latest/javascript-api/jslib/)
  do not have TypeScript definitions, so you must `@ts-expect-error` those.
  Rollup processes the TypeScript, and then we execute the transpiled code with
  k6.
- Follow typical Openverse JavaScript code style and development procedures, but
  keep in mind k6's special requirements, and the fact that
  [it doesn't have a "normal" JavaScript execution environment](https://grafana.com/docs/k6/latest/javascript-api/).
  - An important example of these special requirements are that k6 depends on
    the scenario functions being exported from the executed test script. **This
    is why the frontend `.test.ts` files all `export * from "./scenarios"`**,
    otherwise the functions referenced by name in the generated scenarios would
    not be available for execution by k6 from the test file.
- Test suites should be placed in namespaced directories, and then named in the
  pattern `{scenario}.test.ts`. This format is mandatory for build and execution
  scripts to function as intended. For example, `src/frontend/search-en.test.ts`
  has the `frontend` namespace and `search-en` is the scenario name. "Scenario
  name" may also refer to a _group_ of scenarios, as it does in the case of
  `src/frontend/all.test.ts`, which executes all frontend scenarios.
- Use
  [k6 `-e` to pass environment variables](https://grafana.com/docs/k6/latest/using-k6/environment-variables/#environment-variables)
  that test code relies on to create flexible tests. For example, use this
  method to write tests that can target any hostname where the target service
  might be hosted.
