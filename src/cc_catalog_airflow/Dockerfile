FROM python:3.7-buster

ENV AIRFLOW_HOME=/usr/local/airflow
ENV PATH=/usr/local/airflow/.local/bin:$PATH
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

RUN set -ex \
  && apt-get -yqq update \
  && apt-get -yqq upgrade \
  && apt-get -yqq install build-essential libpq-dev
RUN useradd -m -d ${AIRFLOW_HOME} airflow
USER airflow

WORKDIR  /usr/local/airflow
ADD ./requirements.txt /usr/local/airflow

RUN pip install --user -r requirements.txt

CMD airflow initdb && airflow scheduler & airflow webserver
