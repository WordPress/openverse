#!/bin/bash
set -e
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

# Set up API database and upstream
docker-compose exec -T "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py migrate --noinput"
# Create a superuser and a user for integration testing
# Not that the Python code uses 4 spaces for indentation after the tab that is stripped by <<-
docker-compose exec -T "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py shell <<-EOF
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
docker-compose exec -T "$DB_SERVICE_NAME" /bin/bash -c "psql <<-EOF
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

docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql <<-EOF
	DROP TABLE IF EXISTS content_provider CASCADE;
	EOF"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -t content_provider -h db | psql"

# Load sample data for images
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql <<-EOF
	\copy image \
			(identifier, created_on, updated_on, ingestion_type, provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, width, height, filesize, license, license_version, creator, creator_url, title, meta_data, tags, watermarked, last_synced_with_source, removed_from_source, filetype, category) \
		from './sample_data/sample_images.csv' \
		with (FORMAT csv, HEADER true);
	REFRESH MATERIALIZED VIEW image_view;
	EOF"

# Load sample data for audio
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql <<-EOF
	\copy audio \
			(identifier, created_on, updated_on, ingestion_type, provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, filetype, duration, bit_rate, sample_rate, category, genres, audio_set, set_position, alt_files, filesize, license, license_version, creator, creator_url, title, meta_data, tags, watermarked, last_synced_with_source, removed_from_source) \
		from './sample_data/sample_audio.csv' \
		with (FORMAT csv, HEADER true);
	REFRESH MATERIALIZED VIEW audio_view;
	EOF"

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

# Clear source cache since it's out of date after data has been loaded
docker-compose exec -T "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-image\" | redis-cli"
docker-compose exec -T "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-audio\" | redis-cli"
