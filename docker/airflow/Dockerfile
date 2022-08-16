# Cannot use $PYTHON_VERSION because that is overwritten by the base image
# with the patch version (we only care about major and minor version)
ARG PROJECT_PY_VERSION

FROM python:${PROJECT_PY_VERSION}-slim

# Build-time arguments, with sensible defaults
ARG REQUIREMENTS_FILE=requirements_prod.txt

# Path configurations
ENV AIRFLOW_HOME=/usr/local/airflow
ENV DAGS_FOLDER=${AIRFLOW_HOME}/openverse_catalog/dags
ENV PYTHONPATH=${DAGS_FOLDER}
ENV PATH=/usr/local/airflow/.local/bin:$PATH

# Container optimizations
ENV PIPNOCACHEDIR=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_COLOR=1

# Airflow/workflow configuration
ENV OUTPUT_DIR=/var/workflow_output/
ENV AIRFLOW__CORE__DAGS_FOLDER=${DAGS_FOLDER}
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

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

ARG AIRFLOW_VERSION=2.3.3
WORKDIR  ${AIRFLOW_HOME}
# Always add the prod req because the dev reqs depend on it for deduplication
COPY ${REQUIREMENTS_FILE} requirements_prod.txt ${AIRFLOW_HOME}/
COPY docker/airflow/wait_for_db.py /opt/airflow/

# args go out of scope when a new build stage starts so it must be redeclared here
ARG PROJECT_PY_VERSION

# https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PROJECT_PY_VERSION}.txt"

RUN pip install --user -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

COPY docker/airflow/entrypoint.sh /opt/airflow/entrypoint.sh

ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
CMD ["server"]
