# Openverse Vale configuration

Openverse runs Vale using
[Vale's PyPI distribution](https://pypi.org/project/vale/). This allows our Vale
version to be tracked in this directory's `pyproject.toml`, meaning tools like
Renovate will be aware of and update it automatically.

This approach to running Vale is intended specifically for running inside `ov`,
and will likely not work outside `ov`. Synced styles are kept in `ov`'s `opt`
directory, which prevents downloaded styles from appearing within the project
files on a contributor's computer.

For more information about this motivation to avoid lists of sensitive terms in
the Openverse monorepo, refer to the README at
[WordPress/openverse-sensitive-terms](https://github.com/WordPress/openverse-sensitive-terms).

To run Vale with Openverse's configuration, use the just recipe:

```bash
ov just .vale/run
```

Typically, it is unnecessary to run Vale directly, as pre-commit automatically
runs Vale on each commit. You only need to run Vale directly when iterating on
changes to Openverse's Vale configuration.

Refer to the `_files` recipe [in the `justfile`](./justfile) to identify which
files we currently check with Vale. A comment on the recipe explains the
rationale for that choice. The list of files will ideally expand in the future
to include all textual content in the repository.
