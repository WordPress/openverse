#cloud-boothook
#/bin/bash

# Set up environment-specific configuration
export DJANGO_DATABASE_NAME="cccatalog"
export DJANGO_DATABASE_USER="deploy"
export DJANGO_DATABASE_PASSWORD="${database_password}"
export DJANGO_DATABASE_HOST="${database_host}"

# Install dependencies
yum -y install git python3-3.7.0-0.16.b3.amzn2.0.1 gcc python3-setuptools python3-devel postgresql-devel
git clone https://github.com/creativecommons/cccatalog-api.git ~/cccatalog-api
pip3 install -r ~/cccatalog-api/requirements.txt
easy_install uwsgi

# Kick off the server
useradd -m uwsgi
mkdir -p /var/log/uwsgi/
touch -p /var/log/uwsgi/cccatalog-api.log
chown -R uwsgi /var/log/uwsgi

uwsgi --chdir=~/cccatalog-api \
      --master \
      --pidfile=/tmp/cccatalog-api.pid \
      --daemonize=/var/log/uwsgi/cccatalog-api.log \
      --uid=uwsgi
      --socket=127.0.0.1:8080
