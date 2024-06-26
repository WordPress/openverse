# syntax=docker/dockerfile:1

# Automatically build image using Python version specified in the `Pipfile`.
ARG INDEXER_WORKER_PY_VERSION

##################
# Python builder #
##################

FROM docker.io/python:${INDEXER_WORKER_PY_VERSION} as builder

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# - Install system packages needed for building Python dependencies
# - Install PDM to install Python dependencies
RUN apt-get update \
      && apt-get install -y python3-dev \
      && rm -rf /var/lib/apt/lists/* \
    && pip install pdm~=2.14

# Copy the Pipenv files into the container
COPY pyproject.toml pdm.lock ./

# Pass additional arguments when installing Python packages with PDM
ARG PDM_INSTALL_ARGS='--no-editable'

# Install Python dependencies into a new virtualenv
RUN pdm install --check --frozen-lockfile $PDM_INSTALL_ARGS

####################
# Indexer worker #
####################

FROM docker.io/python:${INDEXER_WORKER_PY_VERSION}-slim as indexer_worker

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Activate the virtualenv
ENV PATH="/.venv/bin:$PATH"

ENV PYTHONPATH="$PYTHONPATH:/indexer_worker/"
# TLDEXTRACT fails to cache in /home/supervisord, set its cache to /tmp instead
ENV TLDEXTRACT_CACHE="/tmp/python-tldextract"

WORKDIR /indexer_worker

# Copy virtualenv from the builder image
COPY --from=builder /.venv /.venv

# - Install system packages needed for running Python dependencies
#   - libpq-dev: required by `psycopg2`
# - Create directory for holding worker state
RUN apt-get update \
      && apt-get install -y curl libpq-dev \
      && rm -rf /var/lib/apt/lists/* \
      && mkdir /worker_state

# Create a non-root user
RUN useradd ingestionu
RUN chown ingestionu /worker_state
USER ingestionu

# Copy code into the final image
COPY --chown=ingestionu . /indexer_worker/

# Expose Gunicorn server to indexer worker Falcon app
EXPOSE 8003

ARG SEMANTIC_VERSION
ENV SENTRY_RELEASE=$SEMANTIC_VERSION

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "api:api"]
