#! /usr/bin/env bash

set -e

# Define system packages here
# These are packages we assume exist in the base environment

dnf_packages=(
    # required by some python package; contributors should use git on their host
    git

    # required by some pre-commit hooks for node-gyp
    g++

    # command runner
    just

    # CLI for parsing JSON
    jq

    # find commands
    which

    # read man pages inside ov
    mandoc

    # Node.js
    nodejs npm

    # Python
    python3.12 pipx

    # Docker for interacting with the host's docker socket
    docker-ce-cli docker-buildx-plugin docker-compose-plugin
)

pipx_packages=(
    # HTTP CLI like cURL but with better ergonomics
    httpie

    # Postgres CLI client
    pgcli

    # Python package management
    pdm pipenv

    # git pre-commit hook automation
    pre-commit
)

npm_packages=(
    # Node.js runtime version management
    n

    # Node.js ecosystem defacto package manager version manager tool
    corepack
)

mkdir -p /opt /pipx

dnf -y install dnf-plugins-core
dnf -y config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

dnf -y install "${dnf_packages[@]}"

# Install base pipx and npm packages globally (i.e., into /usr/local/bin)
pipx install --global "${pipx_packages[@]}"
npm install -g "${npm_packages[@]}"

corepack enable

chmod -Rv 0777 /opt /pipx
