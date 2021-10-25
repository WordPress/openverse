FROM postgres:13.2

ARG PGCLI_VERSION=3.2.0

# Container optimizations
ARG DEBIAN_FRONTEND=noninteractive
ENV PIPNOCACHEDIR=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_COLOR=1

RUN apt-get update && apt-get -yqq upgrade && apt-get -yqq install \
    python3-boto3 \
    postgresql-plpython3-13 \
    python3-pip \
    libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -U pip \
    && pip3 install pgcli==${PGCLI_VERSION}

COPY *.sql /docker-entrypoint-initdb.d/
