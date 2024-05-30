#! /usr/bin/env bash

set -e

volume_name="openverse-dev-env"

if ! docker volume inspect openverse-dev-env 1>/dev/null; then
  docker volume create "$volume_name" 1>/dev/null
fi

run_args=(
  -i
  --rm
  --env "OPENVERSE_PROJECT=$OPENVERSE_PROJECT"
  --env "TERM=xterm-256color"
  --network host
  # Bind the repo to the same exact location inside the container so that pre-commit
  # and others don't get confused about where files are supposed to be
  -v "$OPENVERSE_PROJECT:$OPENVERSE_PROJECT:rw,z"
  --workdir "$OPENVERSE_PROJECT"
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
  run_args+=(-t)
fi

case "$OSTYPE" in
linux*)
  run_args+=(--user "$UID:$(getent group docker | cut -d: -f3)")
  ;;
darwin*)
  # noop, just catching them to avoid the fall-through error case
  ;;
*)
  printf "Openverse development is only supported on Linux and macOS hosts. Please use WSL to run the Openverse development environment under Linux on Windows computers." >/dev/stderr
  exit 1
  ;;
esac

host_pnpm_store="$(pnpm store path 2>/dev/null || echo)"

# Share the pnpm cache with the container, if it's available locally
if [ "$host_pnpm_store" != "" ]; then
  pnpm_home="$(dirname "$host_pnpm_store")"
  run_args+=(
    --env PNPM_HOME="$pnpm_home"
    -v "$pnpm_home:$pnpm_home:rw,z"
  )
fi

# Share the PDM cache with the container, if it's available locally
# --quiet so PDM doesn't repeatedly fill the console with update messages
# if they're enabled
if [ "$(pdm config --quiet install.cache)" == "True" ]; then
  host_pdm_cache="$(pdm config --quiet cache_dir)"
  run_args+=(
    --env "PDM_CACHE_DIR=$host_pdm_cache"
    -v "$host_pdm_cache:$host_pdm_cache:rw,z"
  )
fi

docker run "${run_args[@]}" openverse-dev-env:latest "$@"
