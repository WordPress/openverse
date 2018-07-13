#!/bin/bash

# Set up Docker daemon
yum -y update
yum -y install docker
# Allows ec2-user to run docker commands
sudo usermod -a -G docker ec2-user
service docker start

# Run the synchronizer
docker pull creativecommons/elasticsearch_syncer:${docker_tag}
docker run -t \
-e AWS_ACCESS_KEY_ID="${aws_access_key_id}" \
-e AWS_SECRET_ACCESS_KEY="${aws_secret_access_key}" \
-e ELASTICSEARCH_URL="${elasticsearch_url}" \
-e ELASTICSEARCH_PORT="${elasticsearch_port}" \
-e AWS_REGION="${aws_region}" \
-e DATABASE_HOST="${database_host}" \
-e DATABASE_USER="deploy" \
-e DATABASE_PASSWORD="${database_password}" \
-e DATABASE_NAME="openledger" \
-e DATABASE_PORT="${database_port}" \
-e DB_BUFFER_SIZE="${db_buffer_size}" \
-e COPY_TABLES="${copy_tables}" \
-e SYNCER_POLL_INTERVAL="${poll_interval}" \
creativecommons/elasticsearch_syncer:${docker_tag} &