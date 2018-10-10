#!/bin/bash

# Set up Docker daemon
sudo yum -y update
sudo yum -y install docker
# Allows ec2-user to run docker commands
sudo usermod -a -G docker ec2-user
service docker start

# Start graylog and local database
docker run --name mongo -d mongo:3
docker run --link mongo --link elasticsearch \
    -p 9000:9000 -p 12201:12201 -p 514:514 \
    -e GRAYLOG_WEB_ENDPOINT_URI="http://0.0.0.0:9000/api" \
    -e GRAYLOG_PASSWORD_SECRET=${graylog_password} \
    -e GRAYLOG_ELASTICSEARCH_HOSTS=${elasticsearch_host} \
    -d graylog/graylog:2.4