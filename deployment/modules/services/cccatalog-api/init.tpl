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
export SEMANTIC_VERSION="$${SEMANTIC_VERSION}"
EOF
source /etc/environment
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

# Set up static content
mkdir -p /var/api_static_content/static

# Kick off the server
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
      --http=:8080 \
      --enable-threads \
      --wsgi-file=./cccatalog/wsgi.py \
      --static-map=/static=/var/api_static_content/static \
      --offload-threads=%k

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