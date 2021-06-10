FROM postgres:13.2
ENV POSTGRES_USER=deploy
ENV POSTGRES_PASSWORD=deploy
ENV POSTGRES_DB=openledger
ADD 0001_airflow_user_db.sql /docker-entrypoint-initdb.d
ADD 0002_aws_s3_mock.sql /docker-entrypoint-initdb.d
ADD 0003_openledger_image_schema.sql /docker-entrypoint-initdb.d
ADD 0004_openledger_image_view.sql /docker-entrypoint-initdb.d
ADD 0005_openledger_old_image_schema.sql /docker-entrypoint-initdb.d
RUN apt-get -y update && apt-get -y install python3-boto3 postgresql-plpython3-13
