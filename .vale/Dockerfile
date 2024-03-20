FROM jdkato/vale:v2.30.0

WORKDIR /vale
COPY .vale.ini .

RUN vale sync

COPY styles styles

ENTRYPOINT ["vale", "--config=/vale/.vale.ini"]
