# Subpackages

## Node.js packages

Openverse uses `pnpm` workspaces to facilitate collecting multiple Node.js
projects into a single repository. This section documents the individual
packages and how to add/maintain them.

```{toctree}
:titlesonly:
:glob:
:maxdepth: 1

js/*/index
```

```{caution}
Openverse does not currently have any method for publishing packages to NPM.
```

### Running package scripts

Run scripts for individual packages using `ov just p {package} {script}`. For
example, to run tests for the `eslint-plugin`, run:

```
ov just p eslint-plugin test:unit
```

This also works for the Nuxt frontend as an alternative to
`ov just frontend/run`:

```
ov just p frontend dev
```

### Adding new packages

The easiest way to create a new package is to copy an existing one and modify
the details to match the needs. To create a new `@openverse/license-parsing`
package, for example, we would do the following:

1. Copy `packages/js/eslint-plugin` to `packages/js/license-parsing`
2. Update `packages/js/license-parsing/package.json` to remove unneeded
   dependencies and update the package name
3. Delete the code in `packages/js/license-parsing/src`, update any relevant
   configuration (`babel.config.js`, etc) and write the code for the new package
   🎉

To reference the package as a dependency in another workspace package (the
frontend or any other package), add it as a dependency using the `workspace:`
syntax:

```json
{
  "dependencies": {
    "@openverse/eslint-plugin": "workspace:*"
  }
}
```

`pnpm` will automatically use the package code as it exists in the package's
directory. Changes to the file defined as `main` in the `package.json` for the
package will be reflected in other packages that depend on it.

````{note}
If a package depends on another, you must add the depended package's build
routine into the dependent package's build. For example, if the frontend
depended on the `@openverse/license-parsing` package, we would need to
add a watcher to build that package in the frontend's `dev` and `build` scripts.
This can be facilitated using `npm-run-all`'s `run-p`. e.g.:

```json
{
  "scripts": {
    "build-deps": "pnpm --filter license-parsing run build --watch",
    "dev": "run-p build-deps dev:only"
  }
}
```
````

All new packages should name their unit-test script `test:unit`. Our CI
recursively runs `test:unit` for all pnpm workspaces to ensure tests pass.

## Python packages

Openverse also maintains smaller Python packages for code sharing and reuse
between the Python stacks. This section documents the individual packages and
how to add/maintain them.

```{toctree}
:titlesonly:
:glob:
:maxdepth: 1

python/*/index
```

```{caution}
Openverse does not currently have any method for publishing packages to PyPI.
```
