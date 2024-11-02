# syntax=docker/dockerfile:1

FROM postgres:13.16 AS db

ARG PGCLI_VERSION

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1
ENV PIPX_BIN_DIR=/usr/local/bin

# Enable stop-on-error
# https://www.postgresql.org/docs/current/app-psql.html
#ENV PGOPTIONS="-c on_error_stop=on"
RUN echo "\set ON_ERROR_STOP on" >> /root/.psqlrc

RUN apt-get update \
    && apt-get install -yqq --no-install-recommends \
      python3-boto3 \
      postgresql-plpython3-13 \
      libpq-dev \
      pipx \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && pipx install pgcli==${PGCLI_VERSION}

COPY *.sql /docker-entrypoint-initdb.d/
