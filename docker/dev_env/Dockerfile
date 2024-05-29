FROM docker.io/library/fedora:latest

# Dependency explanations
# - git: required by some python package; contributors should use git on their host
# - gcc, make: required by some pre-commit hooks for node-gyp
# - perl: used in linting
# - bash: used for scripts
# - python: language runtime
# - python-pipx: python CLI app installer
# - docker*: used to interact with host docker socket
# - nodejs, npm: language runtime and dependency manager (system npm required by node-based pre-commit hooks)
# - just: command runner
# - n: nodejs distribution manager
# - pdm, pipenv: Python package managers
# - pre-commit: pre-commit hook manager
RUN dnf -y install dnf-plugins-core \
  && dnf -y config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo \
  && dnf -y install \
  git bash perl curl gcc just \
  python3.12 pipx \
  nodejs npm \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
  && useradd -m opener -G docker \
  && npm install -g n corepack \
  && corepack enable

USER opener

# pipx installed tools are user-dependent, so install these after switching to opener
RUN pipx install pdm pre-commit

ENV PATH="/home/opener/.local/bin:${PATH}"

# Avoid overwriting `.venv`'s from the host
ENV PDM_VENV_IN_PROJECT="False"

ENV N_PREFIX="/home/opener/.local/share/n"
ENV PATH="${N_PREFIX}/bin:${PATH}"

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/bin/sh"]
