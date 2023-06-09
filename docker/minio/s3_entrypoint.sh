# Create empty buckets on every container startup
# Note: $0 is included in the exec because "/bin/bash -c" swallows the first
# argument, so it must be re-added at the beginning of the exec call
#!/bin/bash
set -euxo pipefail
for b in ${BUCKETS_TO_CREATE//,/ }; do
  echo "Making bucket $b" && mkdir -p /data/"$b"
done
exec "$@"
