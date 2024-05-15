#! /usr/bin/env sh

# kudos to https://patorjk.com/software/taag/#p=display&f=Big&t=Openverse for the ASCII art
cat <<'EOF'
Welcome to...

   ____
  / __ \
 | |  | |_ __   ___ _ ____   _____ _ __ ___  ___
 | |  | | '_ \ / _ \ '_ \ \ / / _ \ '__/ __|/ _ \
 | |__| | |_) |  __/ | | \ V /  __/ |  \__ \  __/
  \____/| .__/ \___|_| |_|\_/ \___|_|  |___/\___|
        | |
        |_|

This script will check your local development environment for the tools required to work on Openverse.

If anything is missing, it will let you know, and provide a suggestion for where to find it.
EOF

missing_deps_list=""

add_missing_dep() {
  missing_deps_list="- $1\\n$missing_deps_list"
}

mktitle() {
  echo "====== $* ======"
}

linux_just_install_suggestion="
Try installing 'just' using your OS's package manager: https://github.com/casey/just?tab=readme-ov-file#packages

For debian or debian-derived systems (like Ubuntu) that do not have makedeb configured,
'just' also provides pre-built binaries. However, you'll need to manually keep them updated:

https://github.com/casey/just?tab=readme-ov-file#pre-built-binaries

Alternatively, you may prefer using the 'just-install' NPM package, endorsed by the 'just' project:

https://github.com/brombal/just-install#readme
"

macos_just_install_suggestion="
'just' is available through homebrew: https://formulae.brew.sh/formula/just
"

py_install_suggestion="
$(mktitle Python language)

Python 3.11 or later could not be found on your system.
Please update or install Python according to the instructions from the Python Foundation:
"

case $(uname -o) in
GNU/Linux*)
  py_install_suggestion="$py_install_suggestion\nhttps://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python"
  just_install_suggestion="$linux_just_install_suggestion"
  ;;

Darwin)
  py_install_suggestion="$py_install_suggestion\nhttps://docs.python.org/3/using/mac.html#getting-and-installing-python"
  just_install_suggestion="$macos_just_install_suggestion"
  ;;

*)
  printf "Openverse development is only supported on Linux and macOS. Windows users must use WSL to run the Openverse development environment."
  exit 1
  ;;

esac

supress_output() {
  "$@" 2>/dev/null 1>/dev/null
}

if ! supress_output which python3; then
  add_missing_dep "Python 3.11 or greater"
  printf "\n\n%b\n" "$py_install_suggestion"
fi

if ! supress_output which just; then
  add_missing_dep "Just command runner"
  printf "\n\n%b\nThe 'just' command runner could not be found on your system.%b" \
    "$(mktitle \'just\' command runner)" \
    "$just_install_suggestion"
fi

docker_install_suggestion="
$(mktitle Docker container runtime)

Docker is missing from your system. Install it and Docker compose using Docker's instructions.

Docker engine: https://docs.docker.com/engine/install/
Docker compose: https://docs.docker.com/compose/install/

Podman is not currently supported for Openverse development.
"

compose_install_suggestion="
$(mktitle Docker compose plugin)

Docker compose is missing from your system. Install it using Docker's instructions:

https://docs.docker.com/compose/install/
"

if ! supress_output which docker; then
  add_missing_dep "Docker container runtime"
  printf "\n%b" "$docker_install_suggestion"
else
  if ! supress_output docker compose; then
    add_missing_dep "Docker compose v2 plugin"
    printf "\n%b" "$compose_install_suggestion"
  fi
fi

pnpm_install_suggestion="
$(mktitle pnpm Node.js package manager)

pnpm is missing from your system, and corepack was unavailable to automatically install it using standard Node.js tooling.

For ease of use, Corepack is highly recommended and is the most flexible approach to Node.js package manager installation.

Refer to Corepack's documentation for installation instructions: https://github.com/nodejs/corepack?tab=readme-ov-file#how-to-install

Alternatively, to install pnpm directly, refer to pnpm's installation instructions: https://pnpm.io/installation#on-posix-systems
"

if ! supress_output which pnpm; then
  if supress_output which corepack; then
    printf "\n\nEnabling corepack in the repository for pnpm!\n"
    corepack enable pnpm
  else
    add_missing_dep "pnpm package manager"
    printf "\n%b" "$pnpm_install_suggestion"
  fi
fi

if [ "$missing_deps_list" != "" ]; then
  printf "\n\nI detected the following missing dependencies:\n%b\n" "$missing_deps_list"
  exit 1
else
  printf "
Congrats! Your system appears to be all set up for Openverse development!

Try running 'just install' followed by 'just up' and then 'just init'.

Further setup instructions can be found in the quick start guide.
The guide also includes instructions for setting up individual parts of the Openverse stack.

https://docs.openverse.org/general/quickstart.html
"
  exit 0
fi
