# syntax=docker/dockerfile:1

# Automatically build image using Python version specified in `pyproject.toml`
ARG API_PY_VERSION

##################
# Audio waveform #
##################

# Pull image `realies/audiowaveform` from Docker Hub and alias as `awf`
FROM docker.io/realies/audiowaveform:1.10.1 AS awf

# Identify dependencies of the `audiowaveform` binary and move them to `/deps`,
# while retaining their folder structure
RUN ldd /usr/local/bin/audiowaveform | tr -s '[:blank:]' '\n' | grep '^/' | \
  xargs -I % sh -c 'mkdir -p $(dirname deps%); cp % deps%;'

##################
# Python builder #
##################

FROM docker.io/python:${API_PY_VERSION} AS builder

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# - Install system packages needed for building Python dependencies
# - Create a virtualenv inside `/venv`
# - Install PDM to install Python dependencies
RUN apt-get update \
  && apt-get install -yqq --no-install-recommends \
    python3-dev \
    git \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && pip install pdm~=2.14

# Copy subpackages from additional build-context 'packages'
COPY --from=packages openverse-attribution ./packages/python/openverse-attribution

# Copy the Python project manifest and PDM lockfile into the container
COPY pyproject.toml pdm.lock ./

# Pass additional arguments when installing Python packages with PDM
ARG PDM_INSTALL_ARGS='--no-editable'

# Install Python dependencies into a new virtualenv
RUN pdm install --check --frozen-lockfile $PDM_INSTALL_ARGS

#######
# API #
#######

FROM docker.io/python:${API_PY_VERSION}-slim AS api

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Activate the virtualenv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /api

COPY api/utils/fonts/SourceSansPro-Bold.ttf /usr/share/fonts/truetype/SourceSansPro-Bold.ttf

# Copy virtualenv from the builder image
COPY --from=builder /.venv /.venv

# Copy `audiowaveform` dependencies. This is unreliable as we use
# The `latest` version of the audiowaveform image which may introduce
# dependency changes which *could* have a different directory structure.
# If this step is failing, try adding the logging in this commit to help
# update the dependency paths:
# https://github.com/WordPress/openverse/commit/6cd8e3944a1d4ba7a3e80705b969a6a50eb75b5a
COPY --from=awf /deps/lib/ /lib/
COPY --from=awf /deps/usr/ /usr/

# Copy `audiowaveform` binary
COPY --from=awf /usr/local/bin/audiowaveform /usr/local/bin

# - Install system packages needed for running Python dependencies
#   - libexempi8: required for watermarking
# - Create directory for dumping API logs
RUN apt-get update \
  && apt-get install -yqq --no-install-recommends \
    curl \
    libexempi8 \
    postgresql-client \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /var/log/openverse_api/openverse_api.log

# Create a folder for placing static files
RUN mkdir /static

# Create a non-root user, and make it the owner of the static dir created above
RUN useradd --create-home opener \
  && chown -R opener /static
USER opener

# Copy code into the final image
COPY --chown=opener --from=packages openverse-attribution /packages/python/openverse-attribution/
COPY --chown=opener . /api/

# Collect static assets, these are used by the next stage, `nginx`
RUN env \
  SETUP_ES="False" \
  DJANGO_SECRET_KEY="any string" \
  CANONICAL_DOMAIN="" \
  python manage.py collectstatic

# Add the release version to the docker container
ARG SEMANTIC_VERSION
ENV SEMANTIC_VERSION=$SEMANTIC_VERSION
ENV SENTRY_RELEASE=$SEMANTIC_VERSION

# Exposes
# - 8000: Dev server for API Django app
EXPOSE 8000

# Wait for ES to accept connections
ENTRYPOINT ["./run.sh"]

CMD ["python", "run.py"]

#########
# NGINX #
#########

FROM docker.io/nginx:1.26.0-alpine as nginx

LABEL org.opencontainers.image.source = "https://github.com/WordPress/openverse"

WORKDIR /app

COPY nginx.conf.template /etc/nginx/templates/openverse-api.conf.template

# Copy static files from `api` target
COPY --from=api /static /app/static

# Only environment variables with this prefix will be available in the template
ENV NGINX_ENVSUBST_FILTER="DJANGO_NGINX_"
ENV DJANGO_NGINX_ENVIRONMENT="local"
# Add the release version to the docker container
ARG SEMANTIC_VERSION
ENV DJANGO_NGINX_GIT_REVISION=$SEMANTIC_VERSION
