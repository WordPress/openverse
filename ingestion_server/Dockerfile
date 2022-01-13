##################
# Python builder #
##################

FROM python:3.10 as builder

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

####################
# Ingestion server #
####################

FROM python:3.10-slim as ing

ENV PYTHONBUFFERED=1
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
      && apt-get install -y curl libpq-dev \
      && rm -rf /var/lib/apt/lists/* \
    && mkdir /worker_state

# Copy code into the final image
COPY . /ingestion_server/

# Exposes
# - 8001: Gunicorn server for `ingestion_server` Falcon app
# - 8002: Gunicorn server for `indexer_worker` Falcon app
EXPOSE 8001 8002

# CMD is set from Docker Compose
