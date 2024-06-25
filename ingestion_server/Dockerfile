# syntax=docker/dockerfile:1

# Automatically build image using Python version specified in the `Pipfile`.
ARG INGESTION_PY_VERSION

##################
# Python builder #
##################

FROM docker.io/python:${INGESTION_PY_VERSION} as builder

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

# - Install system packages needed for building Python dependencies
# - Create a virtualenv inside `/venv`
# - Install Pipenv to install Python dependencies
RUN apt-get update \
    && apt-get install -yqq --no-install-recommends \
      python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /venv \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock /

# Install Python dependencies system-wide (uses the active virtualenv)
RUN pipenv install --system --deploy --dev

####################
# Ingestion server #
####################

FROM docker.io/python:${INGESTION_PY_VERSION}-slim as ing

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

ENV PYTHONPATH="$PYTHONPATH:/ingestion_server/"
# TLDEXTRACT fails to cache in /home/supervisord, set its cache to /tmp instead
ENV TLDEXTRACT_CACHE="/tmp/python-tldextract"

WORKDIR /ingestion_server

# Copy virtualenv from the builder image
COPY --from=builder /venv /venv

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
RUN useradd ingestionu
RUN chown ingestionu /worker_state
USER ingestionu

# Copy code into the final image
COPY --chown=ingestionu . /ingestion_server/

# Exposes
# - 8001: Gunicorn server for `ingestion_server` Falcon app
# - 8002: Gunicorn server for `indexer_worker` Falcon app
EXPOSE 8001 8002

ARG SEMANTIC_VERSION
ENV SENTRY_RELEASE=$SEMANTIC_VERSION

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "api:api"]
