FROM python:3.6

ENV PYTHONBUFFERED 1

RUN mkdir /es-syncer
WORKDIR /es-syncer
ADD requirements.txt /es-syncer/
RUN pip install -r requirements.txt
