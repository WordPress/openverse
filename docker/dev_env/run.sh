#! /usr/bin/env bash

set -e

container_name="openverse-dev_env"
image_name="$container_name"
volume_name="openverse_dev-env"

if ! docker volume inspect "$container_name" &>/dev/null; then
  docker volume create "$volume_name" 1>/dev/null
fi

shared_args=(
  -i
  --env "OPENVERSE_PROJECT=$OPENVERSE_PROJECT"
  --env "TERM=xterm-256color"
  # Avoid overwriting `.venv`'s from the host
  --env "PDM_VENV_IN_PROJECT=False"
  # Install global pipx packages separate from user packages
  # Prevents permissions issue with packages installed as root
  # when running packages.sh
  --env "PIPX_GLOBAL_HOME=/pipx"
  --workdir "$(pwd)"
)

run_args=(
  -d
  --name "$container_name"
  --network host
  # Bind the repo to the same exact location inside the container so that pre-commit
  # and others don't get confused about where files are supposed to be
  -v "$OPENVERSE_PROJECT:$OPENVERSE_PROJECT:rw,z"
  # Save the /opt directory of the container so we can reuse it each time
  --mount "type=volume,src=$volume_name,target=/opt"
  # Expose the host's docker socket to the container so the container can run docker/compose etc
  -v /var/run/docker.sock:/var/run/docker.sock
)

# When running `ov` directly, `-t 0` will show that stdin is available, so
# we should provision a TTY in the docker container (making it possible to
# interact with the container directly)
# However, when running in pre-commit (for example), there is no TTY, and
# docker run will complain if `-t` requests a TTY when the execution
# environment doesn't have one to attach.
# In other words, only tell Docker to attach a TTY to the container when
# there's one to attach in the first place.
if [ -t 0 ]; then
  shared_args+=(-t)
fi

_cmd=("$@")

if [ "$1" == "sudo" ]; then
  # Remove sudo
  # Linux hosts will run the command as root instead in the user check below.
  # macOS hosts don't need to bother, they're always running as root in the container anyway
  _cmd=("${@:2}")
fi

case "$OSTYPE" in
linux*)
  docker_group=$(getent group docker | cut -d: -f3)
  if [ "$1" == "sudo" ]; then
    user_id="0"
  else
    user_id="$UID"
  fi
  shared_args+=(--user "$user_id:$docker_group")
  ;;

darwin*)
  # noop, just catching them to avoid the fall-through error case
  ;;

*)
  printf "Openverse development is only supported on Linux and macOS hosts. Please use WSL to run the Openverse development environment under Linux on Windows computers." >/dev/stderr
  exit 1
  ;;

esac

# Ensure cache directory uses, `ov clean` destroys it
mkdir -p "$DEV_ENV"/.cache

if command -v pnpm &>/dev/null; then
  if [ ! -f "$DEV_ENV"/.cache/pnpm-store-path ]; then
    # This command can be slow, so cache the response
    # Should be safe, it's rare to change this, ov clean removes it otherwise
    pnpm store path >"$DEV_ENV"/.cache/pnpm-store-path
  fi

  host_pnpm_store=$(cat "$DEV_ENV"/.cache/pnpm-store-path)

  # Share the pnpm cache with the container, if it's available locally
  if [ -n "$host_pnpm_store" ]; then
    pnpm_home="$(dirname "$host_pnpm_store")"
    shared_args+=(--env PNPM_HOME="$pnpm_home")
    run_args+=(-v "$pnpm_home:$pnpm_home:rw,z")
  fi
fi

if command -v pdm &>/dev/null; then
  if [ ! -f "$DEV_ENV"/.cache/pdm-cache-path ]; then
    # These commands can be slow, so cache the response
    # Should be safe, it's rare to change this
    if [ "$(pdm config --quiet install.cache)" == "True" ]; then
      pdm config --quiet cache_dir >"$DEV_ENV"/.cache/pdm-cache-path
    else
      echo "" >"$DEV_ENV"/.cache/pdm-cache-path
    fi
  fi

  host_pdm_cache=$(cat "$DEV_ENV"/.cache/pdm-cache-path)

  # Share the PDM cache with the container, if it's available locally
  # --quiet so PDM doesn't repeatedly fill the console with update messages
  # if they're enabled
  if [ -n "$host_pdm_cache" ]; then
    shared_args+=(--env "PDM_CACHE_DIR=$host_pdm_cache")
    run_args+=(-v "$host_pdm_cache:$host_pdm_cache:rw,z")
  fi
fi

existing_container_id=$(docker ps -a --filter name="$container_name" -q)
existing_container_image_id=$(docker ps -a --format="{{ .Image }}" -f name="$container_name")

run_container() {
  docker run "${shared_args[@]}" "${run_args[@]}" "$image_name":latest 1>/dev/null
}

if [ -z "$existing_container_id" ]; then
  run_container
elif [ "$existing_container_image_id" != "$image_name":latest ]; then
  # If the existing container is running the latest image, it will be referred to as the ":latest" tag
  # Otherwise, $existing_container_image_id will be the actual image ID hash, in which case we aren't running the latest available image
  # Redirect output to stderr so that it isn't hidden but still won't affect piping or otherwise capturing stdout when running `ov`.
  printf "Detected a new version of the base image. Stopping the existing container and starting a new one with the latest base image.\n" >/dev/stderr
  docker stop "$existing_container_id" 1>/dev/stderr
  docker rm "$existing_container_id" 1>/dev/stderr
  run_container
else
  # Do not need to bother checking if the container is already running, docker start
  # is a noop in that case with no adverse effects
  docker start "$existing_container_id" 1>/dev/null
fi

docker exec "${shared_args[@]}" "$container_name" python3 "$OPENVERSE_PROJECT"/docker/dev_env/exec.py "${_cmd[@]}"
