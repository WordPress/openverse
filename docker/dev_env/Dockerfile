FROM docker.io/library/fedora:latest

# We want to keep all important things in `/opt` as we will preserve the
# `/opt` directory as a volume.

# location where pipx installs its tools
ENV PIPX_HOME="/opt/pipx"
# location where pipx symlinks the binaries, must be on the path
ENV PIPX_BIN_DIR="/opt/pipx/bin"
# location where PDM installs Python interpreters
ENV PDM_PYTHONS="/opt/pdm/bin"
# location where `n` installs Node.js versions
ENV N_PREFIX="/opt/n"
# location where pre-commit stores environments
ENV PRE_COMMIT_HOME="/opt/pre-commit"

# Add tooling installed in custom locations to `PATH`.
ENV PATH="${N_PREFIX}/bin:${PDM_PYTHONS}:${PIPX_BIN_DIR}:${PATH}"

# Dependency explanations:
# - git: required by some python package; contributors should use git on their host
# - perl: used in linting
# - gcc: required by some pre-commit hooks for node-gyp
# - just: command runner
# - which: locate a program file in `PATH`
# - pipx: Python CLI app installer
# - nodejs: language runtime (includes npm but not Corepack)
# - docker*: used to interact with host Docker socket
#
# pipx dependencies:
# - pdm, pipenv: Python package managers
# - pre-commit: Git pre-commit and pre-push hook manager
#
# Node dependencies:
# - n: Node.js distribution manager
# - corepack: Node.js package-manager-manager
RUN dnf -y install dnf-plugins-core \
  && dnf -y config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo \
  && dnf -y install \
    git \
    perl \
    gcc \
    just \
    which \
    pipx \
    nodejs \
    docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
  && pipx install \
    pdm pipenv  \
    pre-commit \
  && npm install -g \
    n \
    corepack \
  && corepack enable

# Avoid overwriting `.venv`'s from the host
ENV PDM_VENV_IN_PROJECT="False"

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/bin/sh"]
