FROM python:3.7-buster

ENV AIRFLOW_HOME=/usr/local/airflow
ENV PATH=/usr/local/airflow/.local/bin:$PATH

RUN apt-get -yqq update \
  && apt-get -yqq upgrade \
  && apt-get -yqq install build-essential libpq-dev libffi-dev
RUN useradd -m -d ${AIRFLOW_HOME} airflow
USER airflow

WORKDIR  /usr/local/airflow
ADD ./requirements.txt /usr/local/airflow

RUN pip install --user -r requirements.txt

CMD airflow initdb && airflow scheduler & airflow webserver
