#! /usr/bin/env bash

set -e

chmod -R 0777 /opt /pipx

if [ ! -d "$OPENVERSE_PROJECT"/.git ]; then
  printf "Repository not mounted to container!\n"
  exit 1
fi

cd "$OPENVERSE_PROJECT" || exit 1

corepack install

if [ -z "$(n ls 2>/dev/null)" ]; then
  printf "Installing the specific Node JS version required by Openverse frontend\n"
  n install auto
fi

if [[ -n $PNPM_HOME && ! -L $PNPM_BIN ]]; then
  ln -s "$PNPM_HOME" "$PNPM_BIN"
fi

if ! PYTHON_311=$(uv python find 3.11 2>/dev/null); then
  printf "Installing the specific Python version required for pipenv environments\n"
  uv python install 3.11
  PYTHON_311=$(uv python find 3.11)
fi
export PYTHON_311

if [ ! -x /usr/local/bin/python3.11 ]; then
  ln -s "$PYTHON_311" /usr/local/bin/python3.11
fi

if [ -z "$(command -v pipenv)" ]; then
  # Install pipenv with the specific python version required by environments
  # still using it, otherwise it gets confused about which dependencies to use
  pipx install pipenv --python "$PYTHON_311"
fi
