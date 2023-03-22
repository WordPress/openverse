##################
# Audio waveform #
##################

FROM realies/audiowaveform:latest AS awf

# Identify dependencies of the `audiowaveform` binary and move them to `/deps`,
# while retaining their folder structure
RUN ldd /usr/local/bin/audiowaveform | tr -s '[:blank:]' '\n' | grep '^/' | \
    xargs -I % sh -c 'mkdir -p $(dirname deps%); cp % deps%;'

##################
# Python builder #
##################

FROM python:3.10 AS builder

ENV PYTHONBUFFERED=1
# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

# - Install system packages needed for building Python dependencies
# - Create a virtualenv inside `/venv`
# - Install Pipenv to install Python dependencies
RUN apt-get update \
      && apt-get install -y python3-dev \
      && rm -rf /var/lib/apt/lists/* \
    && python -m venv /venv \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock ./

# Install Python dependencies system-wide (uses the active virtualenv)
RUN pipenv install --system --deploy --dev

#########
# Nginx #
#########

# This target assumes that the build host has run `manage.py collectstatic`
# `just api/collectstatic` is provided as a convenient alias for running it the expected way

FROM nginx:1.23.3-alpine as nginx

LABEL org.opencontainers.image.source = "https://github.com/WordPress/openverse"

WORKDIR /app

COPY nginx.conf.template /etc/nginx/templates/openverse-api.conf.template
COPY /static /app/static

# Only environment variables with this prefix will be available in the template
ENV NGINX_ENVSUBST_FILTER="DJANGO_NGINX_"
ENV DJANGO_NGINX_ENVIRONMENT="local"
# Add the release version to the docker container
ARG SEMANTIC_VERSION
ENV DJANGO_NGINX_GIT_REVISION=$SEMANTIC_VERSION

#######
# API #
#######

FROM python:3.10-slim as api

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

ENV PYTHONBUFFERED=1
# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

WORKDIR /api

ADD catalog/api/utils/fonts/SourceSansPro-Bold.ttf /usr/share/fonts/truetype/SourceSansPro-Bold.ttf

# Copy virtualenv from the builder image
COPY --from=builder /venv /venv

# Copy `audiowaveform` dependencies
COPY --from=awf /deps /
# Copy `audiowaveform` binary
COPY --from=awf /usr/local/bin/audiowaveform /usr/local/bin

# - Install system packages needed for running Python dependencies
#   - libexempi8: required for watermarking
#   - libpq-dev: required by `psycopg2`
# - Create directory for dumping API logs
RUN apt-get update \
      && apt-get install -y curl libpq-dev libexempi8 postgresql-client \
      && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/openverse_api/openverse_api.log

# Create a non-root user
RUN useradd --create-home opener
USER opener

# Copy code into the final image
COPY --chown=opener . /api/

# Add the release version to the docker container
ARG SEMANTIC_VERSION
ENV SEMANTIC_VERSION=$SEMANTIC_VERSION

# Exposes
# - 8000: Dev server for API Django app
# - 3000: Sphinx live server
EXPOSE 8000 3000

# Wait for ES to accept connections
ENTRYPOINT ["./run.sh"]

# Run Django dev server, can be overridden from Docker Compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
