# Openverse Vale configuration

The Openverse Vale configuration is not meant to be used directly. Instead, it
should be used via the published Docker image, or a locally-built image when
testing Vale configuration changes.

To run using the published image, run the following from the monorepo root
directory:

```
$ just .vale/run
```

To run using a locally-built image, run the following recipe, which builds and
then runs the image:

```
$ just .vale/run-local
```

Refer to the `CI_CONFIG` variable [in the justfile](./justfile) to identify
which files we currently check with Vale. A comment on the variable explains the
rationale for that choice. The list of files will ideally expand in the future
to include all textual content in the repository.
