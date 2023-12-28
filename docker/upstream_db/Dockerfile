# syntax=docker/dockerfile:1

FROM postgres:13.10 as db

ARG PGCLI_VERSION=4.0.1

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Enable stop-on-error
# https://www.postgresql.org/docs/current/app-psql.html
#ENV PGOPTIONS="-c on_error_stop=on"
RUN echo "\set ON_ERROR_STOP on" >> /root/.psqlrc

RUN apt-get update \
    && apt-get -yqq install \
      python3-boto3 \
      postgresql-plpython3-13 \
      python3-pip \
      libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -U pip pgcli==${PGCLI_VERSION}

COPY *.sql /docker-entrypoint-initdb.d/
