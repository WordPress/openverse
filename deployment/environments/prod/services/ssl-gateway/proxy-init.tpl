#!/bin/bash

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
    - /var/log/nginx/*.log
    - /var/log/letsencrypt/*.log*
  fields:
    system: ssl-proxy
    environment: prod

output.logstash:
  hosts: ["graylog.private:5044"]
EOF
sudo systemctl start filebeat

# Install certbot
cd /tmp
wget -O epel.rpm –nv \
https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install -y ./epel.rpm
sudo yum install -y python2-certbot-nginx.noarch

# Set up nginx. The SSL stuff is handled by certbot.
sudo amazon-linux-extras install nginx1.12
sudo cat << EOF > /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        server_name  graylog.creativecommons.engineering;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
          proxy_set_header Host $http_host;
          proxy_set_header X-Forwarded-Host $host;
          proxy_set_header X-Forwarded-Server $host;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Graylog-Server-URL https://$server_name/api;
          proxy_pass http://graylog.private:9000;
        }
    }
}
EOF

# Get an SSL certificate and start the server.
sudo certbot --nginx --email=webmaster@creativecommons.org \
--agree-tos \
--no-eff-email \
--non-interactive \
--domains=graylog.creativecommons.engineering

# Certbot has a tendency to start nginx outside of systemctl, so we have to
# kill all nginx instances after it runs.
sudo pkill nginx

sudo systemctl start nginx