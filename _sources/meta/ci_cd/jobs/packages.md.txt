# Packages jobs

## `js-package-checks`

Runs a matrix for various checks of workspace packages in the `packages/js`
directory using the following `package.json` scripts.

| Name        | Script      |
| ----------- | ----------- |
| `build`     | `build`     |
| `unit_test` | `test:unit` |

```{note}
Not all packages in `packages/js/` necessarily need to define both or any of
these scripts. `pnpm run -r` will safely ignore packages that do not define a
given script and just run it for the ones that do.
```

Since this is a required check for a matrix job, it has a bypass counterpart.
Refer to the documentation for [bypass jobs](/meta/ci_cd/flow.md#bypass-jobs).
