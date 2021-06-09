FROM python:3.9

ARG CCCATALOG_STORAGE_BUCKET
ENV SCRIPT_DIR=/app

WORKDIR ${SCRIPT_DIR}
ADD ./create_bucket.py ${SCRIPT_DIR}
RUN pip install moto[server]

CMD python create_bucket.py & moto_server s3 -H 0.0.0.0
