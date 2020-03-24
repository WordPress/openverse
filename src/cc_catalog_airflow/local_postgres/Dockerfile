FROM postgres:10.9
ENV POSTGRES_USER=deploy
ENV POSTGRES_PASSWORD=deploy
ENV POSTGRES_DB=openledger
ADD ./openledger_image_schema.sql /docker-entrypoint-initdb.d
ADD ./airflow_user_db.sql /docker-entrypoint-initdb.d
