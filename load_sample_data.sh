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
  bash -c "$(psql_cmd $UPSTREAM_DB_SERVICE_NAME) <<-EOF
    DELETE FROM $1;
		\copy $1 \
			from '/sample_data/sample_$1.csv' \
			with (FORMAT csv, HEADER true);
		REFRESH MATERIALIZED VIEW $1_view;
		EOF"
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

if [ $index_count = 0 ]; then
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

function check_index_exists {
  index=$1
  curl \
    -s \
    --output /dev/null \
    -I \
    -w "%{http_code}\n" \
    "http://$ES_SERVICE_NAME:9200/$index" | grep -v 404 || true
}

# Check if init indexes already exist
image_init_exists=$(check_index_exists image-init)
audio_init_exists=$(check_index_exists audio-init)

if [ $image_init_exists ] && [ $audio_init_exists ]; then
  echo 'Both init indexes already exist. Use `just recreate` to fully recreate your local environment.' > /dev/stderr
  exit 1
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

bash -c "$(psql_cmd $DB_SERVICE_NAME) <<-EOF
	DELETE FROM content_provider;
	INSERT INTO content_provider
		(created_on, provider_identifier, provider_name, domain_name, filter_content, media_type)
	VALUES
		(now(), 'flickr', 'Flickr', 'https://www.flickr.com', false, 'image'),
		(now(), 'stocksnap', 'StockSnap', 'https://stocksnap.io', false, 'image'),
		(now(), 'freesound', 'Freesound', 'https://freesound.org/', false, 'audio'),
		(now(), 'jamendo', 'Jamendo', 'https://www.jamendo.com', false, 'audio'),
		(now(), 'wikimedia_audio', 'Wikimedia', 'https://commons.wikimedia.org', false, 'audio');
	EOF"

#############
# Ingestion #
#############

function _curl_post {
  curl \
    -X POST \
    -s \
    -H 'Content-Type: application/json' \
    -d "$1" \
    -w "\n" \
    "http://$INGESTION_SERVER_SERVICE_NAME:8001/task"
}

function wait_for_index {
  index=${1:-image}
  suffix=${2:-init}
  # Wait for no relocating shards. Cannot wait for index health to be green
  # as it is always yellow in the local environment.
  echo "Waiting for index $index-$suffix..."
  curl \
    -s \
    --output /dev/null \
    --max-time 10 \
    "http://$ES_SERVICE_NAME:9200/_cluster/health/$index-$suffix?wait_for_no_relocating_shards=true"
}

function ingest_test_data {
  echo "Loading $1 test data..."
  _curl_post "{\"model\": \"$1\", \"action\": \"LOAD_TEST_DATA\"}"
}

function ingest_upstream {
  model=${1:-image}
  suffix=${2:-init}
  echo "Ingesting $model-$suffix from upstream..."
  _curl_post "{\"model\": \"$model\", \"action\": \"INGEST_UPSTREAM\", \"index_suffix\": \"$suffix\"}"
}

function promote {
  model=${1:-image}
  suffix=${2:-init}
  alias=${3:-image}

  echo "Promoting $model-$suffix to $alias..."
  _curl_post "{\"model\": \"$model\", \"action\": \"PROMOTE\", \"index_suffix\": \"$suffix\", \"alias\": \"$alias\"}"
}


# Load search quality assurance data.
ingest_test_data audio
sleep 2

ingest_test_data image
sleep 2

# Ingest and index the data
if [ -z "$audio_init_exists" ]; then
  ingest_upstream audio init
  wait_for_index audio init
  promote audio init audio
  wait_for_index audio
fi

if [ -z "$image_init_exists" ]; then
  # Image ingestion is flaky; but usually works on the next attempt
  set +e
  while true; do
    ingest_upstream image init
    if wait_for_index image init
    then
      break
    fi
    ((c++)) && ((c==3)) && break
  done
  set -e

  promote image init image
  wait_for_index image
fi

#########
# Redis #
#########

python3 manage.py shell <<-EOF
from django.core.cache import cache
source_caches = ['image', 'audio']
cache.delete_many([f'sources-{sc}' for sc in source_caches])
EOF
