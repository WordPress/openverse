FROM python:3.9-slim

# Build-time arguments, with sensible defaults
ARG REQUIREMENTS_FILE=requirements_prod.txt

# Path configurations
ENV AIRFLOW_HOME=/usr/local/airflow
ENV PATH=/usr/local/airflow/.local/bin:$PATH

# Container optimizations
ENV PIPNOCACHEDIR=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_COLOR=1

# Airflow/workflow configuration
ENV OUTPUT_DIR=/var/workflow_output/
ENV AIRFLOW__CORE__DAGS_FOLDER=${AIRFLOW_HOME}/openverse_catalog/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
# TODO: Test if moving this to .env changes anything!
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=aws_default
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://openverse-airflow-logs


RUN apt-get update && apt-get -yqq upgrade && apt-get -yqq install \
    build-essential \
    libpq-dev \
    libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -d ${AIRFLOW_HOME} airflow && \
    mkdir -p ${OUTPUT_DIR} && \
    chown airflow:airflow ${OUTPUT_DIR}
USER airflow

ARG AIRFLOW_VERSION=2.2.4
WORKDIR  ${AIRFLOW_HOME}
# Always add the prod req because the dev reqs depend on it for deduplication
COPY ${REQUIREMENTS_FILE} requirements_prod.txt ${AIRFLOW_HOME}/
COPY docker/airflow/wait_for_db.py /opt/airflow/

# https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.9.txt"

RUN pip install --user -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

COPY docker/airflow/entrypoint.sh /opt/airflow/entrypoint.sh

ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
CMD ["server"]
