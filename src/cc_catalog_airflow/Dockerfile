FROM python:3.7-buster

ENV AIRFLOW_HOME=/usr/local/airflow
ARG OUTPUT_DIR=/tmp/workflow_output/
ENV PATH=/usr/local/airflow/.local/bin:$PATH
ARG REQUIREMENTS_FILE=requirements_prod.txt

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

RUN pip install --user -r ${REQUIREMENTS_FILE}

CMD python wait_for_db.py && \
  airflow db init && \
  (airflow scheduler & airflow webserver)
