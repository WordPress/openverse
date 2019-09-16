#!/bin/bash

set -e
set -x

while [[ "$(curl --insecure -s -o /dev/null -w '%{http_code}' http://es:9200/)" != "200" ]]
do
  echo "Waiting for Elastic Search connection."
  sleep 2
done

exec "$@"
