#! /usr/bin/env bash

# Place common shared utility functions here
# Functions, not aliases, must be used. Aliases are not expanded in scripts
# and as such will not be available in `entrypoint.sh` when the command
# passed to the docker run is evaluated. That means that `j` below, for example,
# wouldn't work if using `ov j`. However, as a function, it does work.

# Personal aliases and utilities should go in an .ovprofile file at the monorepo root

j() {
  just "$@"
}
