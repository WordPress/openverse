#! /usr/bin/env bash

set -e
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"
ES_SERVICE_NAME="${ES_SERVICE_NAME:-es}"
INGESTION_SERVER_SERVICE_NAME="${INGESTION_SERVER_SERVICE_NAME:-ingestion_server}"

###############
# Upstream DB #
###############

function psql_cmd {
  echo "psql postgresql://deploy:deploy@$1/openledger"
}

# Load sample data
function load_sample_data {
  eval "$(psql_cmd "$UPSTREAM_DB_SERVICE_NAME")" <<-EOF
    DELETE FROM $1;
		\copy $1 \
			from '/sample_data/sample_$1.csv' \
			with (FORMAT csv, HEADER true);
		REFRESH MATERIALIZED VIEW $1_view;
		EOF
}

load_sample_data image
load_sample_data audio

#######
# API #
#######

echo "Waiting for ES... (I will time out after 25 seconds)"
# Wait for ES as Django app depends on it
index_count=$(
  curl \
    -s \
    --retry 5 \
    --retry-connrefused \
    --retry-delay 5 \
    "http://$ES_SERVICE_NAME:9200/_cat/indices" | wc -l
)

if [ "$index_count" = 0 ]; then
  # if indexes exist, then we don't need to wait for ES to initialise
  # if they don't exist, however, then we will need to hold on a second for ES
  # to be ready to start ingestion
  # This ensures the script can be re-run without hanging on waiting for an
  # ES cluster health status that will never materialise after the first run
  curl \
    -s \
    --output /dev/null \
    "http://$ES_SERVICE_NAME:9200/_cluster/health?wait_for_status=green&timeout=2s"
fi

# Set up API database and upstream
python3 manage.py migrate --noinput

# Create a superuser and a user for integration testing
bash -c "python3 manage.py shell <<-EOF
from django.contrib.auth.models import User
usernames = ['continuous_integration', 'deploy']
for username in usernames:
    if User.objects.filter(username=username).exists():
        print(f'User {username} already exists')
        continue
    if username == 'deploy':
        user = User.objects.create_superuser(username, f'{username}@example.com', 'deploy')
    else:
        user = User.objects.create_user(username, f'{username}@example.com', 'deploy')
    user.save()
EOF"

eval "$(psql_cmd "$DB_SERVICE_NAME")" <<-EOF
DELETE FROM content_provider;
INSERT INTO content_provider
  (created_on, provider_identifier, provider_name, domain_name, filter_content, media_type)
VALUES
  (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false, 'image'),
  (now(), 'stocksnap', 'StockSnap', 'https://stocksnap.io', false, 'image'),
  (now(), 'freesound', 'Freesound', 'https://freesound.org/', false, 'audio'),
  (now(), 'jamendo', 'Jamendo', 'https://www.jamendo.com', false, 'audio'),
  (now(), 'wikimedia_audio', 'Wikimedia', 'https://commons.wikimedia.org', false, 'audio');
EOF

#############
# Ingestion #
#############

function _curl_post {
  response=$(
    curl \
      -X POST \
      -s \
      -H 'Content-Type: application/json' \
      -d "$1" \
      -w "\n" \
      "http://$INGESTION_SERVER_SERVICE_NAME:8001/task"
  )
  # extract the status_check parameter from the response without needing to install jq
  cat <<EOF | python
import sys
import json

print(json.loads('$response')["status_check"])
EOF
}

function _await_task {
  # This approach to waiting mirrors how the real data_refresh happens
  # and is far more reliable than trying to infer the status of the indexes
  # from ES endpoints
  # Use python here as well to avoid needing to install jq or similar for
  # parsing the response (and to make the parsing _obvious_ as opposed
  # to using grep or sed!)

  status_check=$1
  task_name=$2
  cat <<EOF | python
import json
from urllib.request import urlopen
import time

def is_active():
    r = urlopen('$status_check')
    r_json = json.loads(r.read().decode())
    return r_json["active"]


print('Awaiting $task_name')

# Effectively waits a max of 30ish seconds as each iteration sleeps 1 second
for _ in range(30):
    if not is_active():
        exit(0)
    time.sleep(1)

print('failed')
EOF
}

function ingest_test_data {
  status_check=$(_curl_post "{\"model\": \"$1\", \"action\": \"LOAD_TEST_DATA\"}")
  _await_task "$status_check" "Loading $1 test data..."
}

function ingest_upstream {
  model=${1:-image}
  suffix=${2:-init}
  retry=$3
  status_check=$(_curl_post "{\"model\": \"$model\", \"action\": \"INGEST_UPSTREAM\", \"index_suffix\": \"$suffix\"}")
  e=$(_await_task "$status_check" "Ingesting $model-$suffix from upstream...")
  if [ "$e" = "failed" ] && (( retry > 0 )); then
    ingest_upstream "$model" "$suffix" "$(( retry - 1 ))"
  fi
}

function promote {
  model=${1:-image}
  suffix=${2:-init}
  alias=${3:-image}

  status_check=$(_curl_post "{\"model\": \"$model\", \"action\": \"PROMOTE\", \"index_suffix\": \"$suffix\", \"alias\": \"$alias\"}")
  _await_task "$status_check" "Promoting $model-$suffix to $alias..."
}


# Load search quality assurance data.
ingest_test_data audio
sleep 2

ingest_test_data image
sleep 2

# Ingest and index the data
ingest_upstream audio init
promote audio init audio

ingest_upstream image init 2
promote image init image


#########
# Redis #
#########

python3 manage.py shell <<-EOF
from django.core.cache import cache
source_caches = ['image', 'audio']
cache.delete_many([f'sources-{sc}' for sc in source_caches])
EOF
