FROM python:3.9

ENV AIRFLOW_HOME=/usr/local/airflow
ARG OUTPUT_DIR=/tmp/workflow_output/
ENV PATH=/usr/local/airflow/.local/bin:$PATH
ARG REQUIREMENTS_FILE=requirements_prod.txt
# https://airflow.apache.org/docs/apache-airflow/2.1.2/installation.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-2.1.2/constraints-3.9.txt"


RUN apt-get -yqq update \
  && apt-get -yqq upgrade \
  && apt-get -yqq install build-essential libpq-dev libffi-dev
RUN useradd -m -d ${AIRFLOW_HOME} airflow
USER airflow

RUN mkdir -p ${OUTPUT_DIR}
WORKDIR  ${AIRFLOW_HOME}
ADD ./${REQUIREMENTS_FILE} ${AIRFLOW_HOME}
ADD ./wait_for_db.py ${AIRFLOW_HOME}
ADD ./dags ${AIRFLOW_HOME}/dags

RUN pip install --user -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

CMD python wait_for_db.py && \
  airflow db init && \
  airflow users create -r Admin -u airflow -f Air -l Flow -p airflow --email airflow@example.org && \
  (airflow scheduler & airflow webserver)
