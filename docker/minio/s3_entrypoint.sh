#!/bin/bash
# Create empty buckets on every container startup
set -euxo pipefail
for b in ${BUCKETS_TO_CREATE//,/ }; do
  echo "Making bucket $b" && mkdir -p /data/"$b"
done
exec "$@"
