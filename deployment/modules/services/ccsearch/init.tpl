#!/bin/bash

# Install node.js and other dependencies
curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
sudo yum -y install gcc-c++ make nodejs git

# Configure frontend
export API_URL="${api_url}"

# Clone and build frontend
git clone https://github.com/creativecommons/cccatalog-frontend.git
cd cccatalog-frontend
git checkout ${git_revision}
sudo npm install --unsafe-perm
sudo npm run build
sudo mkdir -p /var/www/ccsearch
sudo cp -r dist/* /var/www/ccsearch/

# Serve frontend
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

    # Compress large responses to save bandwidth and improve latency
    gzip on;
    gzip_min_length 860;
    gzip_vary on;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types application/json text/plain application/javascript;
    gzip_disable "MSIE [1-6]\.";

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen          8080;
        root /var/www/ccsearch/;
        error_page 404 /index.html;
        index index.html;
        server_name     _;
        charset        utf-8;
        client_max_body_size 75M;

        location /healthcheck {
            access_log off;
            return 200;
        }

        location / {
        }
    }
}
EOF
sudo systemctl start nginx