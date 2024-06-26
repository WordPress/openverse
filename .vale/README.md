# Openverse Vale configuration

Openverse runs Vale using Docker. This bypasses the need for contributors to
install the Vale binary on their computers. It also prevents Vale styles getting
downloaded into the repository in clear text, which is critical to avoid lists
of sensitive terms being accidentally too-easily available.

For more information about this motivation to avoid lists of sensitive terms in
the Openverse monorepo, refer to the README at
[WordPress/openverse-sensitive-terms](https://github.com/WordPress/openverse-sensitive-terms).

To run Vale with Openverse's configuration, use the just recipe:

```
$ just .vale/run
```

This recipe _always_ builds Vale. The Openverse Vale docker image is fast to
build, and the most expensive steps are cached. Docker will automatically reuse
the pre-existing image unless there are changes to the Vale configuration.

Typically it is unnecessary to run Vale directly, as pre-commit automatically
runs Vale on each commit. You only need to run Vale directly when iterating on
changes to Openverse's Vale configuration.

Refer to the `VALE_FILES` variable [in the justfile](./justfile) to identify
which files we currently check with Vale. A comment on the variable explains the
rationale for that choice. The list of files will ideally expand in the future
to include all textual content in the repository.
