#!/bin/bash
set -e
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

###############
# Upstream DB #
###############

# Load sample data
function load_sample_data {
  docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" bash -c "psql <<-EOF
    DELETE FROM $1;
		\copy $1 \
			from './sample_data/sample_$1.csv' \
			with (FORMAT csv, HEADER true);
		REFRESH MATERIALIZED VIEW $1_view;
		EOF"
}

load_sample_data "image"
load_sample_data "audio"

#######
# API #
#######

# Set up API database and upstream
docker-compose exec -T "$WEB_SERVICE_NAME" bash -c "python3 manage.py migrate --noinput"
# Create a superuser and a user for integration testing
# Not that the Python code uses 4 spaces for indentation after the tab that is stripped by <<-
docker-compose exec -T "$WEB_SERVICE_NAME" bash -c "python3 manage.py shell <<-EOF
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

# Load content providers
docker-compose exec -T "$DB_SERVICE_NAME" bash -c "psql <<-EOF
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

# Load search quality assurance data.
just ingestion_server/load-test-data "audio"
sleep 2

just ingestion_server/load-test-data "image"
sleep 2

# Ingest and index the data
just ingestion_server/ingest-upstream "audio" "init"
just docker/es/wait-for-index "audio-init"
just ingestion_server/promote "audio" "init" "audio"
just docker/es/wait-for-index "audio"
just ingestion_server/create-and-populate-filtered-index "audio" "init"
just docker/es/wait-for-index "audio-init-filtered"
just ingestion_server/point-alias "audio" "init-filtered" "audio-filtered"
just docker/es/wait-for-index "audio-filtered" "audio-init-filtered"

# Image ingestion is flaky; but usually works on the next attempt
set +e
while true; do
	just ingestion_server/ingest-upstream "image" "init"
	if just docker/es/wait-for-index "image-init"
	then
		break
	fi
	((c++)) && ((c==3)) && break
done
set -e

just ingestion_server/promote "image" "init" "image"
just docker/es/wait-for-index "image"
just ingestion_server/create-and-populate-filtered-index "image" "init"
just docker/es/wait-for-index "image-init-filtered"
just ingestion_server/point-alias "image" "init-filtered" "image-filtered"
just docker/es/wait-for-index "image-filtered" "image-init-filtered"

#########
# Redis #
#########

# Clear source cache since it's out of date after data has been loaded
docker-compose exec -T "$CACHE_SERVICE_NAME" bash -c "echo \"del :1:sources-image\" | redis-cli"
docker-compose exec -T "$CACHE_SERVICE_NAME" bash -c "echo \"del :1:sources-audio\" | redis-cli"
