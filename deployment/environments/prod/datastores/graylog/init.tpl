#!/bin/bash

# Set up Docker daemon
sudo yum -y update
sudo yum -y install docker
# Allows ec2-user to run docker commands
sudo usermod -a -G docker ec2-user
service docker start

# Start graylog and local database
docker run --name mongo -d mongo:3
docker run --link mongo \
-p 9000:9000 -p 12201:12201 -p 514:514 \
-e GRAYLOG_WEB_ENDPOINT_URI="http://graylog.creativecommons.engineering:9000/api" \
-e GRAYLOG_PASSWORD_SECRET="${graylog_password}" \
-e GRAYLOG_ELASTICSEARCH_HOSTS="https://${elasticsearch_host}:443" \
-e GRAYLOG_ROOT_PASSWORD_SHA2="${graylog_sha2}" \
-d graylog/graylog:2.4
