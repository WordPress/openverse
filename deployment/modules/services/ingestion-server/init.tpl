#!/bin/bash

# Set up Docker daemon
yum -y update
yum -y install docker
# Allows ec2-user to run docker commands
sudo usermod -a -G docker ec2-user
service docker start

# Run the synchronizer
docker pull creativecommons/ingestion_server:${docker_tag}
docker run -t \
-p 8001:8001 \
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
-e UPSTREAM_DATABASE_HOST="${upstream_db_host}" \
-e UPSTREAM_DATABASE_PASSWORD="${upstream_db_password}" \
-e DB_BUFFER_SIZE="${db_buffer_size}" \
-e COPY_TABLES="${copy_tables}" \
-e SYNCER_POLL_INTERVAL="${poll_interval}" \
creativecommons/ingestion_server:${docker_tag} &

# Install filebeat collector for centralized logging to Graylog
sudo rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch
sudo tee /etc/yum.repos.d/filebeat.repo <<EOF
[elastic-5.x]
name=Elastic repository for 5.x packages
baseurl=https://artifacts.elastic.co/packages/5.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF
sudo yum install -y filebeat
sudo tee /etc/filebeat/filebeat.yml <<EOF
filebeat.prospectors:
- type: log
  enabled: true
  paths:
    - /var/log/cloud-init-output.log
  fields:
    system: ingestion-server
    environment: ${staging_environment}

output.logstash:
  hosts: ["graylog.private:5044"]
EOF
sudo systemctl start filebeat