#!/bin/bash
# This does *not* allow for testing permissions issues that may come up in real AWS.
# And, if you remove files from /tests/s3-data, you will need to use `just down -v`
# and `just up` or `just recreate` to see the minio bucket without those files.
# Loop through subdirectories mounted to the volume and load them to s3/minio.
# This takes care of filesystem delays on some local dev environments that may make
# minio miss files included directly in the minio volume.
# More info here: https://stackoverflow.com/questions/72867045
set -euxo pipefail

/usr/bin/mc config host add s3 http://s3:5000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
cd /data
for b in */; do
  echo "Loading bucket $b"
  /usr/bin/mc mb --ignore-existing s3/"$b"
  /usr/bin/mc cp --r "$b" s3/"$b"
  /usr/bin/mc ls s3/"$b"
done
exit 0
