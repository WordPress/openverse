#!/usr/bin/env bash

# ABOUT
# =====
# This Bash script runs inside the dev container when it is created for the
# time. Use this space to prepare the dev environment.

# The Node.js feature installs the latest version of pnpm, not the one we want.
# So we enable Corepack to provision the right pnpm version.
npm install -g corepack@0.31.0 && corepack enable pnpm

# Install dependencies for projects that run outside of the Docker context. This
# includes Node.js packages, Python automations and documentation.
just install

# Running lint installs and prepares the hook environments. This saves time when
# the developer needs to run lint.
just lint
