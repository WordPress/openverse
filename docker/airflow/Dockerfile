FROM python:3.9-slim

ARG OUTPUT_DIR=/var/workflow_output/
ARG REQUIREMENTS_FILE=requirements_prod.txt
# https://airflow.apache.org/docs/apache-airflow/2.1.2/installation.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-2.1.2/constraints-3.9.txt"
ENV AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW__CORE__DAGS_FOLDER=${AIRFLOW_HOME}/openverse_catalog/dags
ENV PATH=/usr/local/airflow/.local/bin:$PATH
ENV PIPNOCACHEDIR=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_COLOR=1


RUN apt-get update && apt-get -yqq upgrade && apt-get -yqq install \
    build-essential \
    libpq-dev \
    libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -d ${AIRFLOW_HOME} airflow
USER airflow

WORKDIR  ${AIRFLOW_HOME}
# Always add the prod req because the dev reqs depend on it for deduplication
COPY ${REQUIREMENTS_FILE} requirements_prod.txt wait_for_db.py ${AIRFLOW_HOME}/

RUN pip install --user -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

CMD python wait_for_db.py && \
  airflow db init && \
  airflow users create -r Admin -u airflow -f Air -l Flow -p airflow --email airflow@example.org && \
  (airflow scheduler & airflow webserver)
