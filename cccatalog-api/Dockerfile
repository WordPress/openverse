FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /cccatalog-api
RUN mkdir -p /var/log/cccatalog-api/cccatalog-api.log
RUN apt-get update
RUN apt-get install libexempi3
WORKDIR /cccatalog-api
ADD requirements.txt /cccatalog-api/
ADD cccatalog/api/utils/fonts/SourceSansPro-Bold.ttf /usr/share/fonts/truetype/SourceSansPro-Bold.ttf
RUN pip install -r requirements.txt
