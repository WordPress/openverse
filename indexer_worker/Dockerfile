# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom

# Automatically build image using Python version specified in `pyproject.toml`
ARG INDEXER_WORKER_PY_VERSION

# Get the version from the main justfile
ARG OV_UV_VERSION

FROM ghcr.io/astral-sh/uv:${OV_UV_VERSION} AS uv

##################
# Python builder #
##################

FROM docker.io/python:${INDEXER_WORKER_PY_VERSION} AS builder

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1
# Use the image's Python instead of downloading one
ENV UV_PYTHON_DOWNLOADS=never

# Install system packages needed for building Python dependencies
RUN apt-get update \
    && apt-get install -yqq --no-install-recommends python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /bin/uv

# Copy the Python project manifest and uv lockfile into the container
COPY pyproject.toml uv.lock /

# Pass additional arguments when installing Python packages with uv
ARG UV_SYNC_ARGS=""

# Install Python dependencies into a new virtualenv at `/.venv`
RUN uv sync --locked $UV_SYNC_ARGS

####################
# Indexer worker #
####################

FROM docker.io/python:${INDEXER_WORKER_PY_VERSION}-slim AS indexer_worker

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Activate the virtualenv
ENV PATH="/.venv/bin:$PATH"

ENV PYTHONPATH="/indexer_worker/"
# TLDEXTRACT fails to cache in /home/supervisord, set its cache to /tmp instead
ENV TLDEXTRACT_CACHE="/tmp/python-tldextract"

WORKDIR /indexer_worker

# Copy virtualenv from the builder image
COPY --from=builder /.venv /.venv

# - Install system packages needed for running Python dependencies
#   - libpq-dev: required by `psycopg2`
# - Create directory for holding worker state
RUN apt-get update \
    && apt-get install -yqq --no-install-recommends \
      curl \
      libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /worker_state

# Create a non-root user
RUN useradd ov_user \
    && chown ov_user /worker_state

USER ov_user

# Copy code into the final image
COPY --chown=ov_user . /indexer_worker/

# Expose Gunicorn server to indexer worker Falcon app
EXPOSE 8003

ARG SEMANTIC_VERSION
ENV SENTRY_RELEASE=$SEMANTIC_VERSION

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "api:api"]
