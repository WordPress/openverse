FROM postgres:13.2
ENV POSTGRES_USER=deploy
ENV POSTGRES_PASSWORD=deploy
ENV POSTGRES_DB=openledger
ADD ./openledger_image_schema.sql /docker-entrypoint-initdb.d
ADD ./openledger_old_image_schema.sql /docker-entrypoint-initdb.d
ADD ./openledger_image_view.sql /docker-entrypoint-initdb.d
ADD ./aws_s3_mock.sql /docker-entrypoint-initdb.d
ADD ./airflow_user_db.sql /docker-entrypoint-initdb.d
RUN apt-get -y update && apt-get -y install python3-boto3 postgresql-plpython3-13
