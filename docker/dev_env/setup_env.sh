#! /usr/bin/env bash

set -e

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

pdm config python.install_root "/opt/pdm/python"
pdm config venv.location "/opt/pdm/venvs"

_python3s=(/opt/pdm/python/cpython@3.11.*/bin/python3)

if [ ! -x "${_python3s[0]}" ]; then
  printf "Installing the specific Python version required for pipenv environments\n"
  pdm python install 3.11
  _python3s=(/opt/pdm/python/cpython@3.11.*/bin/python3)
fi

PYTHON_311=${_python3s[0]}
export PYTHON_311

if [ ! -x /usr/local/bin/python3.11 ]; then
  ln -s "$PYTHON_311" /usr/local/bin/python3.11
fi

if [ -z "$(command -v pipenv)" ]; then
  # Install pipenv with the specific python version required by environments
  # still using it, otherwise it gets confused about which dependencies to use
  pipx install pipenv --python "$PYTHON_311"
fi

if [ -n "$PDM_CACHE_DIR" ]; then
  pdm config install.cache on
fi
