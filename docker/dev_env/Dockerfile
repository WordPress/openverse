FROM docker.io/library/fedora:40

# We want to keep all important things in `/opt` as we will preserve the
# `/opt` directory as a volume.

# Set HOME to /opt so XDG-respecting utilities automatically use it
# without additional configuration
# This gets chmodded with wide open permissions, so that
# on Linux hosts, the explicitly passed user (with docker group)
# is able to read/write from here, as well as the root user used by
# macOS hosts (who don't have Docker permissions or host filesystem
# permissions issues to contend with and as such run the container as root)
ENV HOME="/opt"

# location where PDM installs Python interpreters
ENV PDM_PYTHONS="${HOME}/pdm/bin"
# location where `n` installs Node.js versions
ENV N_PREFIX="${HOME}/n"

ENV PIPX_GLOBAL_HOME=/pipx

ENV PNPM_BIN="${HOME}/pnpm"

# Add tooling installed in custom locations to `PATH`.
ENV PATH="${PNPM_BIN}:${N_PREFIX}/bin:${PDM_PYTHONS}:${HOME}/.local/bin:${PATH}"

# Dependency explanations:
# - git: required by some python package; contributors should use git on their host
# - perl: used in linting
# - gcc, g++: required by some pre-commit hooks for node-gyp
# - just: command runner
# - jq: JSON processor
# - which: locate a program file in `PATH`
# - python*: required by some Python libraries for compilation during installation
# - libffi*: required for the Python package cffi
# - pipx: Python CLI app installer
# - nodejs: language runtime (includes npm but not Corepack)
# - docker*: used to interact with host Docker socket
# - postgresql*: required to connect to PostgreSQL databases
#
# pipx dependencies:
# - httpie: CLI HTTP client
# - pdm, pipenv: Python package managers
# - pre-commit: Git pre-commit and pre-push hook manager
# - pgcli: PostgreSQL CLI
#
# Node dependencies:
# - n: Node.js distribution manager
# - corepack: Node.js package-manager-manager
RUN mkdir /pipx \
  && dnf -y install dnf-plugins-core \
  && dnf -y config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo \
  && dnf -y install \
    git \
    g++ \
    just \
    jq \
    which \
    nodejs npm \
    python3.12 python3.12-devel pipx \
    libffi-devel \
    docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
    unzip \
    postgresql postgresql-devel \
  && dnf clean all \
  && pipx install --global \
    httpie \
    pdm pipenv  \
    pgcli \
    pre-commit \
    twine \
  && npm install -g \
    n \
    corepack \
  && corepack enable

# Avoid overwriting `.venv`'s from the host
ENV PDM_VENV_IN_PROJECT="False"

# The fedora container's default entrypoint + command behaviour is to keep running
# so we do not need to modify entrypoint and command to use the container as a
# persistent environment.
