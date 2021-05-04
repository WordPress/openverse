#!/bin/bash

set -e

while [[ "$(curl --insecure -s -o /dev/null -w '%{http_code}' http://es:9200/)" != "200" ]]
do
  echo "Waiting for Elasticsearch connection..."
  sleep 2
done

exec "$@"
