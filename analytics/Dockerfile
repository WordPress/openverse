##################
# Python builder #
##################

FROM python:3.10 as builder

ENV PYTHONBUFFERED 1
# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

# - Install system packages needed for building Python dependencies
#   - librdkafka-dev
# - Create a virtualenv inside `/venv`
# - Install Pipenv to install Python dependencies
RUN apt-get update \
      && apt-get install -y python3-dev librdkafka-dev \
      && rm -rf /var/lib/apt/lists/* \
    && python -m venv /venv \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock ./

# Install Python dependencies system-wide (uses the active virtualenv)
RUN pipenv install --system --deploy --dev

#############
# Analytics #
#############

FROM python:3.10-slim as nl

ENV PYTHONBUFFERED=1
# Activate the virtualenv
ENV PATH="/venv/bin:$PATH"

ENV PYTHONPATH="$PYTHONPATH:/analytics/"

WORKDIR /analytics

# Copy virtualenv from the builder image
COPY --from=builder /venv /venv

# - Install system packages needed for running Python dependencies
#   - librdkafka-dev
#   - libpq-dev: required by `psycopg2`
RUN apt-get update \
      && apt-get install -y libpq-dev librdkafka-dev \
      && rm -rf /var/lib/apt/lists/*

# Exposes
# - 8090: Gunicorn server for `analytics` Falcon app
EXPOSE 8090

# Run Falcon server, can be overridden from Docker Compose
CMD ["gunicorn", "-c", "./gunicorn.conf.py"]
