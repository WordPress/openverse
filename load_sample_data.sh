#! /usr/bin/env bash
set -e
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

while getopts 'c' OPTION; do
  case "$OPTION" in
  c)
    echo "Loading upstream DB data..."
    upstream_only=true
    ;;
  ?)
    echo "Loading all sample data..."
    ;;
  esac
done

###############
# Upstream DB #
###############

function exec_sql {
  echo "$2" | just dc exec -T "$1" psql -AXqt
}

# Load sample data
function load_sample_data {
  exec_sql "$UPSTREAM_DB_SERVICE_NAME" "DELETE FROM $1"
  exec_sql "$UPSTREAM_DB_SERVICE_NAME" "\copy $1 from './sample_data/sample_$1.csv' with (FORMAT csv, HEADER true);"
}

function verify_loaded_data {
  COUNT=$(exec_sql "$UPSTREAM_DB_SERVICE_NAME" "SELECT COUNT(*) FROM $1;")
  if [ "$COUNT" -ne 5000 ]; then
    echo "Error: table $1 count differs from expected."
    exit 1
  fi
}

load_sample_data "image"
verify_loaded_data "image"
load_sample_data "audio"
verify_loaded_data "audio"

# Terminate the script if received flag for only upstream data
if [ "$upstream_only" = true ]; then
  exit 0
fi

#######
# API #
#######

# Set up API database and upstream
just dc exec -T "$WEB_SERVICE_NAME" python3 manage.py migrate --noinput
# Create a superuser and a user for integration testing
# Not that the Python code uses 4 spaces for indentation after the tab that is stripped by <<-
echo "
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
" | just dc exec -T "$WEB_SERVICE_NAME" python3 manage.py shell

# Load content providers
exec_sql "$DB_SERVICE_NAME" "
DELETE FROM content_provider;
INSERT INTO content_provider
	(created_on, provider_identifier, provider_name, domain_name, filter_content, media_type)
VALUES
	(now(), 'flickr', 'Flickr', 'https://www.flickr.com', false, 'image'),
	(now(), 'stocksnap', 'StockSnap', 'https://stocksnap.io', false, 'image'),
	(now(), 'freesound', 'Freesound', 'https://freesound.org/', false, 'audio'),
	(now(), 'jamendo', 'Jamendo', 'https://www.jamendo.com', false, 'audio'),
	(now(), 'wikimedia_audio', 'Wikimedia', 'https://commons.wikimedia.org', false, 'audio');
"

#############
# Ingestion #
#############

# Ingest and index the data
just ingestion_server/ingest-upstream "audio" "init"
just docker/es/wait-for-index "audio-init"
just docker/es/wait-for-count "audio-init"
just ingestion_server/promote "audio" "init" "audio"
just docker/es/wait-for-index "audio"
just docker/es/wait-for-count "audio"
just ingestion_server/create-and-populate-filtered-index "audio" "init"
just docker/es/wait-for-index "audio-init-filtered"
just ingestion_server/point-alias "audio" "init-filtered" "audio-filtered"
just docker/es/wait-for-index "audio-filtered" "audio-init-filtered"

# Image ingestion is flaky; but usually works on the next attempt
set +e
while true; do
  just ingestion_server/ingest-upstream "image" "init"
  if just docker/es/wait-for-index "image-init"; then
    break
  fi
  ((c++)) && ((c == 3)) && break
done
set -e

just docker/es/wait-for-count "image-init"
just ingestion_server/promote "image" "init" "image"
just docker/es/wait-for-index "image"
just docker/es/wait-for-count "image"
just ingestion_server/create-and-populate-filtered-index "image" "init"
just docker/es/wait-for-index "image-init-filtered"
just ingestion_server/point-alias "image" "init-filtered" "image-filtered"
just docker/es/wait-for-index "image-filtered" "image-init-filtered"

#########
# Redis #
#########

# Clear source cache since it's out of date after data has been loaded
docker-compose exec -T "$CACHE_SERVICE_NAME" bash -c 'echo "del :1:sources-image" | redis-cli'
docker-compose exec -T "$CACHE_SERVICE_NAME" bash -c 'echo "del :1:sources-audio" | redis-cli'
