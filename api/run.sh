#!/bin/bash

set -e

es_url="http://${ELASTICSEARCH_URL:-es}:${ELASTICSEARCH_PORT:-9200}/_cluster/health"
while [ "$(curl -s -o /dev/null -w '%{http_code}' "$es_url")" != "200" ]; do
  echo "Waiting for Elasticsearch connection..." && sleep 5
done
echo "Elasticsearch connection established!"

# Run any database migrations
if [ "$DJANGO_MIGRATE_DB_ON_STARTUP" != "False" ]; then
  echo "Running database migrations..."
  python manage.py migrate
fi

exec "$@"
