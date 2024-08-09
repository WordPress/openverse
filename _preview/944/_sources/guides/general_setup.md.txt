# General setup guide

This is an exhaustive list for new developers. Feel free to skip the steps that
you have already done on your own.

## Operating system

```{caution}
Openverse development is currently supported only for UNIX-type environments
(Linux and macOS). Windows is not supported natively, but PRs that enable
Openverse development on Windows, or improve the experience, are welcome.
```

```{tip}
We recommend Windows Subsystem for Linux (WSL) as a viable option.
```

Windows Subsystem for Linux can be a much more versatile and familiar
environment for software development on Windows. Everything from installing
`git` and other dependencies to using command line tools that will be familiar
to the wider community of software developers are more likely to be easier under
WSL. While some parts of some Openverse projects may be able to be developed
under native Windows, you will have a much smoother time with WSL as our command
runners (`just` and `pnpm`) assume a UNIX-type environment (Linux and macOS).

Installation instructions for WSL on Windows 10 and 11 can be found in
Microsoft's
[official documentation](https://docs.microsoft.com/en-us/windows/wsl/install).

## Required setup

The following setup steps are needed to set up a local copy of Openverse and do
not prepare you to contribute code to the project.

### Git

Openverse is Git-tracked. To clone Openverse locally, you will need to install
`git`. Most Linux distributions and macOS will already have this installed, even
if it's not always the latest version. To know if you have Git installed, run
the following command.

```console
$ git --version
```

If you see `git version x.y.z`, you have Git installed. If you see an error, you
need to install it by following the
[official instructions](https://git-scm.com/downloads).

### Python

```{note}
This is only needed for working with the Python stack outside of Docker and for
Python automations.
```

We use Python 3 in the backend of our stack. So to work with that part of the
codebase, you will need Python installed. Most Linux distributions and macOS
will already have this installed, even if it's not always the latest version. To
know if you have Python (specifically version 3) installed, run the following
command.

```console
$ python3 --version
```

If you see `Python x.y.z`, you have Python installed. If you see an error, you
need to install it using [pyenv](https://github.com/pyenv/pyenv) or by following
the [official instructions](https://www.python.org/downloads/).

#### Pipenv

Pipenv helps us provision dependencies for our Python packages and automatically
set up a virtualenv, provided you have the version of Python mentioned in the
`Pipfile` installed and accessible locally.

You can install Pipenv by following the
[official instructions](https://pipenv.pypa.io/en/latest/installation/#installing-pipenv).

### Node.js

```{note}
This is only needed for working with the frontend and for Node.js automations.
```

We use Node.js in the frontend of our stack. So to work with that part of the
codebase, you will need Node.js installed. To know if you have Node.js
installed, run the following command.

```console
$ node --version
```

If you see `vx.y.z`, you have Node.js installed. If you see an error, you need
to install it using [nvm](https://github.com/nvm-sh/nvm) or by following the
[official instructions](https://nodejs.org/en/download/).

#### Corepack

Corepack helps manage package managers for a project. In any Node.js workspace,
like the [`WordPress/openverse`](https://github.com/WordPress/openverse/)
monorepo for example, Corepack will automatically invoke the right version of
the specified package manager, also installing it if needed and not present.

It's a part of Node.js and present in Node.js versions v14.19.0 and v16.9.0
onwards. So no installation is needed.

### Docker

```{note}
This is only needed for working with the Python stack. The Node.js stack runs
on the host.
```

Our Python packages are published as Docker images to make it easier to work
with them locally during development and also make it easier to deploy new
versions in production.

If you run WSL on Windows, you can
[set up Docker Desktop](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers#install-docker-desktop).
If not, you can use one of the many
[installation methods](https://docs.docker.com/engine/install/) officially
supported by Docker.

#### Docker Compose

Docker Compose makes it easy to orchestrate multiple services which we put to
use by orchestrating the external services and also the API, ingestion server
and indexer workers locally during development.

Docker Compose is a part of the Docker Desktop installation. To know if you have
Docker Compose installed, run the following command.

```console
$ docker compose version
```

If you see `Docker Compose version vx.y.z`, you have Docker Compose installed.
If you see an error, you need to install it by following the
[official instructions](https://docs.docker.com/compose/install/).

### `just`

We use `just` as our command runner. It makes it easier to run cumbersome
commands that are generally needed a lot during development, like bringing up
our backend services or linting the codebase.

`just` can be [installed](https://github.com/casey/just#installation) for a host
of operating systems via their respective pacakge managers.

````{tip}
If you run `just` inside the Openverse root repo without a recipe name, you can
see a huge list of all the different recipes present in the project.

```console
$ cd openverse/
$ just
```
````

## Development dependencies

The following setup steps are needed to not just setup Openverse but to also
contribute code to the project.

### GitHub

The source code for Openverse is hosted on GitHub. To contribute to Openverse,
you will also need to [sign up](https://github.com/signup) for a GitHub account.
It's free, and considering how much OSS development happens on GitHub, almost
essential.

#### GitHub CLI

It's not necessary, but we recommended to install the GitHub CLI in your
development environment because it makes it convenient to work with GitHub
workflows like filing issues and opening PRs.

You can install the CLI by following the
[official instructions](https://github.com/cli/cli#installation).

### Text editors/IDEs

A good editor or IDE (integrated development environment) makes a lot of
difference when working with software source code. We recommend VS Code or a
JetBrains IDE because that's what we use day-to-day. Feel free to pick a
different editor if you have a preference.

- [VS Code](https://code.visualstudio.com/) is an option with good
  out-of-the-box support for our entire stack.
- [PyCharm and WebStorm](https://www.jetbrains.com/) are other very popular
  options with lots of bells and whistles.
- [Sublime Text](https://www.sublimetext.com/) is a minimalistic option that can
  get you off the ground quickly with lots of room for expansion through it's
  package system.
- [vim](https://www.vim.org/) and [emacs](https://www.gnu.org/software/emacs/)
  are ubiquitous terminal-based options.

## Optional development setup

The following setup steps are only needed in very specific scenarios.

### coreutils

```{note}
This is only needed on macOS.
```

`coreutils` adds GNU utils to macOS. `timeout` from the package is required. You
can install the
[`coreutils` formula](https://formulae.brew.sh/formula/coreutils) using
[Homebrew](https://brew.sh), which is a package manager for macOS.

### mkcert

```{note}
This is only needed to test SSL locally.
```

To test SSL locally, install `mkcert` (and the corresponding
[NSS](https://firefox-source-docs.mozilla.org/security/nss/index.html) tools) by
following the
[official instruction](https://github.com/FiloSottile/mkcert#installation). You
can run `mkcert -install` to verify your installation.

### OpenSSL

```{note}
This is only need if the `psycopg2` install fails with the `ld: library not
found for -lssl` error when running the project outside Docker.
```

This `psycopg2` package can fail to install on Apple Silicon Macs with the
`ld: library not found for -lssl` error. To rectify this, install `openssl` via
Homebrew and set `LDFLAGS` and `CPPFLAGS` as per the instructions in the output
of the Homebrew installation.
