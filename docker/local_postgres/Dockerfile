FROM postgres:13.2
ARG PGCLI_VERSION=3.2.0
RUN apt-get update && apt-get -yqq upgrade && apt-get -yqq install \
    python3-boto3 \
    postgresql-plpython3-13 \
    python3-pip \
    libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pgcli==${PGCLI_VERSION}

COPY *.sql /docker-entrypoint-initdb.d/
