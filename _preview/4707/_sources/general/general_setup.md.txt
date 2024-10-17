# General setup guide

Openverse maintains a containerised development environment named `ov`, and it
is the only supported method of working with Openverse. `ov` is included in the
repository, and its only dependencies are git, bash, and Docker (or a compatible
container runtime).

```{admonition} Openverse and Windows
:class: caution
Openverse development is currently supported only for UNIX-type environments
(Linux and macOS). Windows is not directly supported, but development may be
possible using Windows Subsystem for Linux (WSL).

Installation instructions for WSL on Windows 10 and 11 can be found in
Microsoft's
[official documentation](https://docs.microsoft.com/en-us/windows/wsl/install).
```

## Dependencies

You must have available on your computer (referred to as the "host system") the
following:

- bash
- git
- Docker (or a compatible container runtime)

On macOS and most popular Linux distributions, bash and git are installed by
default. Most contributors will only need to install Docker or a compatible
container runtime to use `ov`.

[Follow Docker's instructions to install Docker on your host system](https://docs.docker.com/engine/install/).

```{tip}
For Openverse, you'll only need the container runtime, and do not necessarily
need to install additional tools like Docker compose, buildx, and so forth.

While Openverse relies on these tools, they are all installed in the `ov` container,
and therefore do not need to be available on your host system if you won't use
them otherwise.
```

## Up and running

1. Clone the GitHub repository:

```shell
git clone --filter=blob:none https://github.com/WordPress/openverse.git # or your fork
cd ./openverse
```

```{note}
We recommend cloning with the `--filter=blob:none` flag as it dramatically
reduces the filesize and download time by creating a "blobless clone".
You can learn more about these [here](https://gist.github.com/leereilly/1f4ea46a01618b6e34ead76f75d0784b).
```

2. Initialise the `ov` development environment:

```shell
./ov init
```

3. It is strongly recommended to add `ov` to your
   [`PATH`](https://en.wikipedia.org/wiki/PATH_%28variable%29) so that you can
   run it from anywhere without needing to reference it relative to the
   repository root.

   You can do so using a symbolic link, for example:

   ```shell
   ln -s $(git rev-parse --show-toplevel)/ov ~/.local/bin/ov
   ```

   Add `~/.local/bin` to your `PATH` or replace it in the command above with a
   directory on your `PATH`, and _voilà_, you can run `ov` from anywhere without
   needing to reference it relative to the repository.

   ```{caution}
   Throughout the Openverse documentation, we assume `ov` is available for use directly.
   If you cannot add `ov` to your `PATH`, then use a relative reference to it anytime you
   invoke the command (i.e., as in `ov init` above).
   ```

You're done! Run `ov help` to see a list of useful tools, and visit the
quickstart guides for each part of the Openverse project in the list below:

```{toctree}
:maxdepth: 1
:glob:

/frontend/guides/quickstart.md
/api/guides/quickstart.md
/catalog/guides/quickstart.md
/ingestion_server/guides/quickstart.md
```

## `ov` usage

Run `ov help` to read basic documentation for how to use and interact with `ov`.

### Aliases

`ov` has a number of built-in aliases, which are documented and discoverable by
running `ov aliases`.

You may configure your own aliases. Run `ov aliases --help` for documentation.
`ov init` includes an example alias in the generated `.ov_profile.json` to help
you get started.

### Included tools

The containerised `ov` environment includes some excellent general purpose tools
to interact with Openverse's development environment. Here are some important
ones you might see used throughout the documentation:

- [`just`](https://github.com/casey/just) is a command runner. Like `make` but
  with loads of features for writing scripts `make` was never made for. Try
  `ov just` to see all available recipes.
- [`jq`](https://stedolan.github.io/jq/) is a tool for parsing and manipulating
  JSON data. Openverse loves `jq`! Try `ov jq --help` for information.
- [`pdm`](https://pdm-project.org/en/stable/) is a Python package manager. You
  can use it in any Openverse directory to interact with `pyproject.toml` and
  different virtual environments. Try `ov pdm --help` for info.
- [`httpie`](https://httpie.io/docs/cli) is a command line HTTP client. Like
  cURL but with a lot of conveniences and easier to remember. Try `http --help`
  for info.

````{admonition} Bring your own tools
:class: tip

Generally speaking, you should be able to rely on any tools you have on your host system.
You can pipe output to and from `ov` and it should work. For example, the following
will pipe the output of running `ov just api/stats` to your host machine's `less` command.

```shell
ov just api/stats | less
```

It works the other way, too!

```shell
printf '{"hello": "world"}' | ov jq '.hello'
```

You can even pipe from `ov` to `ov`:

```shell
ov just api/stats | ov jq '.[0]'
```

🎉
````

````{admonition} Dive into bash
:class: tip

`ov` includes `bash`, and if you prefer to interact directly with the development environment,
rather than going through `ov` for each command, you can enter into `ov`'s `bash` prompt
like so:

```shell
ov bash
```

Be aware, however, that `ov` aliases **will not work** inside `ov bash`!
````

### Troubleshooting

While `ov` works well to simplify the development environment, you may sometimes
run into problems that you can't figure out.

The first thing to try in these circumstances is `ov doctor`, which attempts
some basic automated troubleshooting steps to fix common issues.

If that does not resolve the problem, the next step is to restart `ov` from
scratch, using `ov clean && ov init`.

If the problem persists, please open an issue in GitHub so that maintainers can
assist in debugging the problem.

### How it works

`ov` itself lives at the repository root, and is just a bash script. Almost all
functionality is implemented through support scripts in `/docker/dev_env`.

`ov` containerises the Openverse development environment by running a persistent
Fedora container and running all development environment tools within this
container. `ov` builds the container from a custom Dockerfile
(`/docker/dev_env/Dockerfile`) that installs the basic tools required for the
Openverse development environment. New tools required for working with Openverse
should be installed using `RUN` in the Dockerfile, along with existing
dependencies.

While `ov` depends on the Docker, Docker compose, and Docker buildx CLI tools,
it is not a docker-in-docker solution. Instead, it relies on the host system's
container runtime to operate. This means the Openverse services, images,
volumes, and so forth, are operating on your host system's container runtime,
which is merely interacted with by the Docker tools within `ov`.

```{note}
Kudos to [distrobox](https://distrobox.it/) for introducing us to the concept
of mapping the host's docker socket into a container.
```

`ov` also runs the container with host networking. This ensures access to things
like the frontend or documentation live site which do not run within the
Openverse docker compose stack, and instead run directly in the `ov` container.

On top of this, in order to ensure messages (especially error messages)
referring to specific files use understandable paths, `ov` maps the Openverse
repository itself to the same path on the container as it is on the host. For
example, if you cloned Openverse to `/home/sara/projects/openverse`, it will be
available at the exact same path inside the container.

```{note}
A similar practice is done with PNPM to share the host cache to the container.
That means if you use PNPM for other projects, you'll still get to benefit from
its speedy install times and disk-space efficiency when working on Openverse.
```

When trying to understand how something works in `ov`, keep in mind that there
are three separate layers of execution:

1. Directly on the host system, which is generally the `ov` script itself, and
   the `/docker/dev_env/run.sh` support script
2. Inside the `ov` container
3. Inside containers from Openverse's Docker compose stack, which still run on
   the host system's container runtime

Note that despite there being three layers, they are not three _nested_ layers.
Rather, they are distinct layers, with the caveat that the second and third
layer are containerised and as such have the container runtime to contend with.

## Text editors/IDEs

A good editor or IDE (integrated development environment) makes a lot of
difference when working with software source code. We recommend VS Code or a
JetBrains IDE because that's what we use day-to-day. Feel free to pick a
different editor if you have a preference.

- [VS Code](https://code.visualstudio.com/) is an option with good
  out-of-the-box support for our entire stack.
- [PyCharm and WebStorm](https://www.jetbrains.com/) are other popular options
  with lots of bells and whistles.
- [Sublime Text](https://www.sublimetext.com/) is a minimalistic option that can
  get you off the ground quickly with lots of room for expansion through its
  package system.
- [vim](https://www.vim.org/) and [emacs](https://www.gnu.org/software/emacs/)
  are ubiquitous terminal-based options.

## Shutting down

1. You can <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.

2. For services running inside Docker, like the API, ingestion server and
   Plausible, use another `just` recipe to bring them down.

   ```bash
   ov just down
   ```

   ````{tip}
   If you include the `-v` flag, all Docker volumes (including their data) will
   be deleted too, which is useful in case you want a fresh start.

   ```bash
   ov just down -v
   ```
   ````

3. For `ov` itself, use `ov stop`.
