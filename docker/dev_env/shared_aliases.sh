#! /usr/bin/env bash

# Aliases are defined as a one-dimensional bash array
# where the odd-or-0 index entries are the aliases, and
# the following even index is the expansion. We cannot use an
# associative array because macOS's bash version is frozen and
# doesn't support them.
# **MULTI-WORD EXPANSIONS MUST BE QUOTED**, plain spaces
# are the separator of bash array entries. See the `nuxt` alias as an example below.
# Aliases are also currently limited in that they cannot reference each other or stack.

declare -a shared_aliases
export shared_aliases

shared_aliases+=(
  j 'just'
  nuxt 'just p frontend dev'
)
