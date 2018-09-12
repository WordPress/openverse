#cloud-boothook
#!/bin/bash

# Set up environment-specific configuration
export VERSION="${api_version}"
export REVISION="${git_revision}"
export SEMANTIC_VERSION="$$VERSION+$${REVISION:0:12}"
cat << EOF > /etc/environment
export DJANGO_DATABASE_NAME="openledger"
export DJANGO_DATABASE_USER="deploy"
export DJANGO_DATABASE_PASSWORD="${database_password}"
export DJANGO_DATABASE_HOST="${database_host}"
export DJANGO_DEBUG_ENABLED="${django_debug_enabled}"
export DJANGO_SECRET_KEY="${django_secret_key}"
export ELASTICSEARCH_URL="${elasticsearch_url}"
export ELASTICSEARCH_PORT="${elasticsearch_port}"
export AWS_REGION="${aws_region}"
export AWS_ACCESS_KEY_ID="${aws_access_key_id}"
export AWS_SECRET_ACCESS_KEY="${aws_secret_access_key}"
export LOAD_BALANCER_URL="${load_balancer_url}"
export VERSION="${api_version}"
export REVISION="${git_revision}"
export REDIS_HOST="${redis_host}"
export REDIS_PASSWORD="${redis_password}"
export ROOT_SHORTENING_URL="${root_shortening_url}"
export DISABLE_GLOBAL_THROTTLING="${disable_global_throttling}"
export SEMANTIC_VERSION="$${SEMANTIC_VERSION}"
EOF
source /etc/environment
# Systemd environment variables file requires a slightly different format
sed 's/^export //' /etc/environment > /etc/systemd_environment

# Install python and git dependencies
yum -y install git python3-3.7.0-0.16.b3.amzn2.0.1 gcc python3-setuptools python3-devel postgresql-devel

# Get the API server. Use a sparse checkout so we only clone the cccatalog-api folder.
mkdir -p /home/ec2-user
cd /home/ec2-user
git init
git config core.sparseCheckout true
git remote add -f origin http://github.com/creativecommons/cccatalog-api.git
echo "cccatalog-api/*" > .git/info/sparse-checkout
git checkout ${git_revision}
cd /home/ec2-user/cccatalog-api

# Install API server dependencies
pip3 install -r /home/ec2-user/cccatalog-api/requirements.txt
easy_install-3.7 uwsgi
pip3 install uwsgitop

# Set up static content
mkdir -p /var/api_static_content/static

# Kick off uWSGI
useradd -m uwsgi
chown -R uwsgi /var/api_static_content/static
python3 manage.py collectstatic --no-input
mkdir -p /var/log/uwsgi/
touch /var/log/uwsgi/cccatalog-api.log
chown -R uwsgi /var/log/uwsgi
chown -R uwsgi /home/ec2-user/cccatalog-api

uwsgi --chdir=/home/ec2-user/cccatalog-api \
      --master \
      --pidfile=/tmp/cccatalog-api.pid \
      --daemonize=/var/log/uwsgi/cccatalog-api.log \
      --uid=uwsgi \
      --socket=:8081 \
      --wsgi-file=./cccatalog/wsgi.py \
      --enable-threads \
      --processes=4 \
      --threads=2 \
      --harakiri=30 \
      --stats=/tmp/stats.socket

# Put nginx in front of uWSGI for static content serving
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

    upstream django {
        server          127.0.0.1:8081;
    }

    server {
        listen          8080;
        server_name     _;
        charset        utf-8;
        client_max_body_size 75M;

        location /static {
            alias /var/api_static_content/static;
        }

        location / {
            uwsgi_pass          django;
            uwsgi_read_timeout  60;
            include             /etc/nginx/uwsgi_params;
        }
    }
}
EOF
sudo systemctl start nginx

# Start periodic tasks using systemd timers and django_cron
# This kicks off a job that intermittently synchronizes traffic statistics
# with the database.
# To monitor the job: journalctl -u django_cron.service
# To monitor the timer: systemctl status django_cron.timer -l
cat << EOF > /etc/systemd/system/django_cron.service
[Unit]
Description=Check that any django_cron jobs need to be run.
[Service]
EnvironmentFile=/etc/systemd_environment
ExecStart=/usr/bin/python3 /home/ec2-user/cccatalog-api/manage.py runcrons
EOF

cat << EOF > /etc/systemd/system/django_cron.timer
[Unit]
Description=Check that any django_cron jobs need to run. The success status and logs of the jobs are stored in the CC Catalog API database in the django_cron table.
Requires=django_cron.service

[Timer]
OnBootSec=10
OnUnitInactiveSec=1min
Unit=django_cron.service

[Install]
WantedBy=timers.target
EOF
systemctl start django_cron.timer