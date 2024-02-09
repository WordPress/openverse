# General setup guide

This is an exhaustive list for new developers. Feel free to skip the steps that
you have already done on your own.

If you already have a development environment set up and want to set up
Openverse on your computer, you can move on to the
[quickstart guide](/general/quickstart.md).

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

## Requirement matrix

Based on which part of the Openverse stack you are contributing to, you might
not need everything mentioned on this page. Refer to this chart to see which
prerequisites are required to get started with your contributions.

| Requirement        | Docs | Ingestion server | API | Frontend       | Management |
| ------------------ | ---- | ---------------- | --- | -------------- | ---------- |
| [Git](#git)        | ✅   | ✅               | ✅  | ✅             | ✅         |
| [`just`](#just)    | ✅   | ✅               | ✅  | ✅             | ✅         |
| [Python](#python)  | ✅   | ➖               | ➖  | ➖             | ✅         |
| [Node.js](#nodejs) | ➖   | ➖               | ➖  | ✅             | ✅         |
| [Docker](#docker)  | ➖   | ✅               | ✅  | ❔[^analytics] | ➖         |

Here ✅ means required, ➖ means not required and ❔ means conditionally
required.

[^analytics]: This is required to run analytics, not required otherwise.

## Required setup

The following setup steps are needed to set up a local copy of Openverse and do
not prepare you to contribute code to the project.

### Git

Openverse is Git-tracked. To clone Openverse locally, you will need to install
`git`. Most Linux distributions and macOS will already have this installed, even
if it's not always the latest version. To know if you have Git installed, run
the following command.

```bash
git --version
```

If you see `git version x.y.z`, you have Git installed. If you see an error, you
need to install it by following the
[official instructions](https://git-scm.com/downloads).

### `just`

We use `just` as our command runner. It makes it easier to run cumbersome
commands that are generally needed a lot during development, like bringing up
our backend services or linting the codebase.

`just` can be [installed](https://github.com/casey/just#installation) for a host
of operating systems via their respective
[package managers](https://github.com/casey/just#packages) or using
[pre-built binaries](https://github.com/casey/just#pre-built-binaries) available
for some operating systems.

````{tip}
If you run `just` inside the Openverse root repo without a recipe name, you can
see a huge list of all the different recipes present in the project.

```bash
cd openverse/
just
```
````

If for some reason, you are unable to install `just`, you can refer to the
`justfile` to see the commands that make up a recipe, and then run those
commands individually in a terminal. It won't be the best user experience, but
it will work just the same.

We also recommend setting up
[shell completions](https://github.com/casey/just#shell-completion-scripts) for
`just` to make it faster to find and run recipes. On macOS with the default Z
shell, Homebrew installs completions for `just` by default.

## Conditional setup

A subset of the following requirements will be required depending on the extent
of your contribution to the project. To see which of these you need, refer to
the [requirement matrix](#requirement-matrix) above.

### Python

```{note}
This is only needed if you are working with the following:

- documentation
- Python automations
- API (outside Docker, for debugging purposes)
- ingestion server (outside Docker, for debugging purposes)
```

We use Python 3 in the backend of our stack. So to work with that part of the
codebase, you will need Python installed. Most Linux distributions and macOS
will already have this installed, even if it's not always the latest version. To
know if you have Python (specifically version 3) installed, run the following
command.

```bash
python3 --version
```

If you see `Python x.y.z`, you have Python installed. If you see an error, you
need to install it using [pyenv](https://github.com/pyenv/pyenv) or by following
the [official instructions](https://www.python.org/downloads/).

#### Pipenv

Pipenv helps us provision dependencies for our Python packages and automatically
set up a virtualenv, provided you have the version of Python mentioned in the
`Pipfile` installed and accessible locally.

You can install Pipenv by following the
[official instructions](https://pipenv.pypa.io/en/latest/installation.html#installing-pipenv).

### Node.js

```{note}
This is only needed if you are working with the following:

- frontend
- Node.js automations
```

We use Node.js in the frontend of our stack. So to work with that part of the
codebase, you will need Node.js installed. To know if you have Node.js
installed, run the following command.

```bash
node --version
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

Enable Corepack in the monorepo root. Then, check if Corepack can discover the
right package manager, pnpm, by running the following commands.

```bash
corepack enable
pnpm --version
```

You should see a version number and no error message.

### Docker

```{note}
This is only needed if you are working with the following:

- API
- ingestion server
- frontend
```

Our Python packages are published as Docker images to make it easier to work
with them locally during development and also make it easier to deploy new
versions in production.

If you run WSL on Windows, you can
[set up Docker Desktop](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers#install-docker-desktop).
If not, you can use one of the many
[installation methods](https://docs.docker.com/engine/install/) officially
supported by Docker.

Note that the building images for the frontend needs an advanced build feature,
namely additional build contexts, that is provided by the
[Buildx plugin](https://docs.docker.com/build/architecture/#buildx). The Buildx
plugin is included in Docker Desktop and all
[installation methods](https://docs.docker.com/engine/install/) for Docker
Engine include steps to also install the Buildx plugin.

To know if your Docker setup is using Buildx, run the following command.

```bash
docker build --help
```

If you see `docker buildx build` under 'Aliases', you have Buildx set up as the
build client.

#### Docker Compose

Docker Compose makes it easy to orchestrate multiple services which we put to
use by orchestrating the external services and also the API, ingestion server
and indexer workers locally during development.

Docker Compose is a part of the Docker Desktop installation. To know if you have
Docker Compose installed, run the following command.

```bash
docker compose version
```

If you see `Docker Compose version vx.y.z`, you have Docker Compose installed.
If you see an error, you need to install it by following the
[official instructions](https://docs.docker.com/compose/install/).

### GitHub

```{note}
This is only needed if you want to contribute code to Openverse. The codebase
can be read, accessed and downloaded without an account.
```

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
- [PyCharm and WebStorm](https://www.jetbrains.com/) are other popular options
  with lots of bells and whistles.
- [Sublime Text](https://www.sublimetext.com/) is a minimalistic option that can
  get you off the ground quickly with lots of room for expansion through it's
  package system.
- [vim](https://www.vim.org/) and [emacs](https://www.gnu.org/software/emacs/)
  are ubiquitous terminal-based options.

## Optional development setup

The following setup steps are only needed in a narrow set of scenarios.

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

### `psycopg2` build prerequisites

```{note}
This is only needed if the `psycopg2` installation fails when running parts of the project outside of Docker.
```

Openverse uses `psycopg2` built from source on the client for compatibility
reasons. You must ensure that
[`psycopg2`'s build prerequisites are fulfilled for the library to install correctly](https://www.psycopg.org/docs/install.html#build-prerequisites).
The linked documentation includes common troubleshooting instrustions for issues
building the library.

#### macOS

The `psycopg2` package can fail to install on Apple Silicon Macs with the
`ld: library not found for -lssl` error. To rectify this, install the
[`openssl` formula](https://formulae.brew.sh/formula/openssl@3) using
[Homebrew](https://brew.sh/) and set `LDFLAGS` and `CPPFLAGS` as per the
instructions in the output of the Homebrew installation.
