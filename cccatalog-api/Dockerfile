FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /cccatalog-api
WORKDIR /cccatalog-api
ADD requirements.txt /cccatalog-api/
RUN pip install -r requirements.txt
