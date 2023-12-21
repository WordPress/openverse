# Openverse Vale configuration

The Openverse Vale configuration is not meant to be used directly. Instead, it
should be used via the published Docker image, or a locally-built image when
testing.

To run using the published image, run the following from the monorepo root
directory:

```
$ docker run --rm -it -v ./documentation:/vale/docs:rw,Z ghcr.io/wordpress/openverse-vale:latest /vale/docs/**/*.md
```

To run using a locally-built image, run the following to build then run the
image:

```
$ cd .vale
$ docker build . -t openverse-vale:local
$ docker run --rm -it -v $PWD/../documentation:/vale/docs:rw,Z openverse-vale:local /vale/docs/**/*.md
```

Vale will not pass if run against all documentation files. Currently, the actual
linting job is only scoped to run
