# syntax=docker/dockerfile:1

# Cannot use $PYTHON_VERSION because that is overwritten by the base image
# with the patch version (we only care about major and minor version)
ARG CATALOG_PY_VERSION
ARG CATALOG_AIRFLOW_VERSION

FROM apache/airflow:slim-${CATALOG_AIRFLOW_VERSION}-python${CATALOG_PY_VERSION} as cat

LABEL org.opencontainers.image.source = "https://github.com/WordPress/openverse"

# Build-time arguments, with sensible defaults
ARG REQUIREMENTS_FILE=requirements-prod.txt

# Path configurations
ENV AIRFLOW_HOME=/opt/airflow
ENV DAGS_FOLDER=${AIRFLOW_HOME}/catalog/dags
ENV PYTHONPATH=${DAGS_FOLDER}
ENV PATH=${AIRFLOW_HOME}/.local/bin:$PATH
ENV IPYTHONDIR=/home/airflow/.cache/ipython

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Airflow/workflow configuration
ENV OUTPUT_DIR=/var/workflow_output/
ENV AIRFLOW__CORE__DAGS_FOLDER=${DAGS_FOLDER}
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV AIRFLOW__WEBSERVER__EXPOSE_STACKTRACE=True

# TODO: Test if moving this to .env changes anything!
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=aws_default
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://openverse-airflow-logs


USER root
RUN apt-get update \
    && apt-get install -yqq --no-install-recommends \
      build-essential \
      libpq-dev \
      libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Create and set the ownership of the cache directory so airflow user can write to them
# These directories are not needed in production but it's easier to perform
# this step here while we're doing it for the output directory
RUN mkdir -p ${OUTPUT_DIR} /home/airflow/.cache && \
    chown airflow ${OUTPUT_DIR} /home/airflow/.cache

USER airflow

WORKDIR  ${AIRFLOW_HOME}
# Always add the prod req because the dev reqs depend on it for deduplication
COPY ${REQUIREMENTS_FILE} requirements-prod.txt ${AIRFLOW_HOME}/

# args go out of scope when a new build stage starts so it must be redeclared here
ARG CATALOG_PY_VERSION
ARG CATALOG_AIRFLOW_VERSION

# https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-${CATALOG_AIRFLOW_VERSION}/constraints-${CATALOG_PY_VERSION}.txt"

RUN pip install -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

COPY entrypoint.sh /opt/airflow/entrypoint.sh
COPY variables.tsv /opt/airflow/variables.tsv

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/opt/airflow/entrypoint.sh"]
