#! /usr/bin/env sh

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

missing_deps=0

linux_just_install_suggestion=$(
  cat <<-'EOF'
Try installing 'just' using your OS's package manager: https://github.com/casey/just?tab=readme-ov-file#packages

For debian or debian-derived systems (like Ubuntu) that do not have makedeb configured,
'just' also provides pre-built binaries. However, you'll need to manually keep them updated:

https://github.com/casey/just?tab=readme-ov-file#pre-built-binaries

Alternatively, you may prefer using the `just-install` NPM package, endorsed by the `just` project:

https://github.com/brombal/just-install#readme
EOF
)

macos_just_install_suggestion="
'just' is available through homebrew: https://formulae.brew.sh/formula/just
"

py_install_suggestion="
====== Python language ======

Python 3.11 or later could not be found on your system. Please update or install Python according to the instructions from the Python Foundation:
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

has_python=0
for python_binary in python python3; do
  if which "$python_binary"; then
    python_version=$("$python_binary" -c "import sys; print(sys.version_info > (3, 11, 0))")
    if [ "$python_version" = "True" ]; then
      has_python=1
      break
    fi
  fi
done

if [ "$has_python" != "1" ]; then
  missing_deps=1

  printf "\n%s\n" "$py_install_suggestion"
fi

if ! which just; then
  missing_deps=1
  printf "\n\n====== 'just' command runner ======\n"
  echo "The 'just' command runner could not be found on your system.$just_install_suggestion"
fi

docker_install_suggestion="

====== Docker container runtime ======

Docker is missing from your system. Install it and Docker compose using Docker's instructions.

Docker engine: https://docs.docker.com/engine/install/
Docker compose: https://docs.docker.com/compose/install/

Podman is not currently supported for Openverse development.
"

compose_install_suggestion="

====== Docker compose plugin ======

Docker compose is missing from your system. Install it using Docker's instructions:

https://docs.docker.com/compose/install/
"

if ! which docker; then
  missing_deps=1
  echo "$docker_install_suggestion"
else
  if ! docker compose 2>/dev/null 1>/dev/null; then
    missing_deps=1
    echo "$compose_install_suggestion"
  fi
fi

pnpm_install_suggestion="
====== pnpm Node.js package manager ======

pnpm is missing from your system, and corepack was unavailable to automatically install it using standard Node.js tooling.

For ease of use, Corepack is highly recommended and is the most flexible approach to Node.js package manager installation.

Refer to Corepack's documentation for installation instructions: https://github.com/nodejs/corepack?tab=readme-ov-file#how-to-install

Alternatively, to install pnpm directly, refer to pnpm's installation instructions: https://pnpm.io/installation#on-posix-systems
"

if ! which pnpm; then
  if which corepack; then
    echo "Enabling corepack for pnpm"
    corepack enable pnpm
  else
    missing_deps=1
    echo "$pnpm_install_suggestion"
  fi
fi

exit "$missing_deps"
