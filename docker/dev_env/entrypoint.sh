#! /usr/bin/env bash

set -e

if [ ! -d "$OPENVERSE_PROJECT"/.git ]; then
  printf "Repository not mounted to container!\n"
  exit 1
fi

cd "$OPENVERSE_PROJECT" || exit 1

suppress_output() {
  "$@" 2>/dev/null 1>/dev/null
}

suppress_output corepack install

if [ -z "$(n ls 2>/dev/null)" ]; then
  printf "Installing the specific Node JS version required by Openverse frontend; this is only necessary the first time the toolkit runs\n"
  n install auto
fi

if [ -n "$PNPM_HOME" ]; then
  export PATH="$PNPM_HOME:$PATH"
fi

pdm config python.install_root "/opt/pdm/python"

_python3s=(/opt/pdm/python/cpython@3.11.*/bin/python3)

if [ ! -x "${_python3s[0]}" ]; then
  printf "Installing the specific Python version required for pipenv environments; this is only necessary the first time the toolkit runs\n"
  pdm python install 3.11
  _python3s=(/opt/pdm/python/cpython@3.11.*/bin/python3)
fi

PYTHON_311=${_python3s[0]}
export PYTHON_311

mkdir -p "$PDM_PYTHONS"

if [ ! -x "$PDM_PYTHONS"/python3.11 ]; then
  ln -s "$PYTHON_311" "$PDM_PYTHONS"/python3.11
fi

if [ -z "$(command -v pipenv)" ]; then
  # Install pipenv with the specific python version required by environments
  # still using it, otherwise it gets confused about which dependencies to use
  pipx install pipenv --python "$PYTHON_311"
fi

if [ -n "$PDM_CACHE_DIR" ]; then
  pdm config install.cache on
fi

_profiles=(
  "$OPENVERSE_PROJECT"/.ovprofile
  "$OPENVERSE_PROJECT"/docker/dev_env/bash_profile.sh
)

for profile in "${_profiles[@]}"; do
  if [ -f "$profile" ]; then
    if grep -q '^alias ' "$profile"; then
      printf "Aliases in %s will not work. Use functions instead." "$profile" >>/dev/stderr
      exit 1
    fi

    # SC1090 cannot be disabled directly
    # Workaround from https://github.com/koalaman/shellcheck/issues/2038#issuecomment-680513830
    # shellcheck source=/dev/null
    source "$profile"
  fi
done

exec "$@"
