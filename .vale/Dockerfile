FROM jdkato/vale:v2.30.0

WORKDIR /vale
COPY .vale.ini .
COPY styles styles

RUN vale sync
