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
docker-compose exec -T "$DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
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

docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	DROP TABLE IF EXISTS content_provider CASCADE;
	EOF"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -t content_provider -U deploy -d openledger -h db | psql -U deploy -d openledger"

# Load sample data for images
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -s -t image -U deploy -d openledger -h db | psql -U deploy -d openledger"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	ALTER TABLE image
		RENAME TO image_view;
	ALTER TABLE image_view
		ADD COLUMN standardized_popularity double precision,
		ADD COLUMN ingestion_type          varchar(1000);

	\copy image_view \
			(identifier, created_on, updated_on, ingestion_type, provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, width, height, filesize, license, license_version, creator, creator_url, title, meta_data, tags, watermarked, last_synced_with_source, removed_from_source, filetype, category, standardized_popularity) \
		from './sample_data/sample_images.csv' \
		with (FORMAT csv, HEADER true);
	EOF"

# Load sample data for audio
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -s -t audio -U deploy -d openledger -h db | head -n -14 | psql -U deploy -d openledger"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	ALTER TABLE audio
		RENAME TO audio_view;
	ALTER TABLE audio_view
		ADD COLUMN standardized_popularity double precision,
		ADD COLUMN ingestion_type          varchar(1000),
		ADD COLUMN audio_set               jsonb;

	\copy audio_view \
			(identifier, created_on, updated_on, ingestion_type, provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, filetype, duration, bit_rate, sample_rate, category, genres, audio_set, audio_set_position, alt_files, filesize, license, license_version, creator, creator_url, title, meta_data, tags, watermarked, last_synced_with_source, removed_from_source, standardized_popularity) \
		from './sample_data/sample_audio.csv' \
		with (FORMAT csv, HEADER true);
	EOF"

# Make one-off modifications to the upstream DB for ingesting audiosets
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	UPDATE audio_view
		SET audio_set_foreign_identifier = audio_set->>'foreign_identifier';

	DROP VIEW IF EXISTS audioset_view;
	CREATE VIEW audioset_view
	AS
		SELECT DISTINCT
            (audio_set ->> 'foreign_identifier')  :: varchar(1000) as foreign_identifier,
            (audio_set ->> 'title')               :: varchar(2000) as title,
            (audio_set ->> 'foreign_landing_url') :: varchar(1000) as foreign_landing_url,
            (audio_set ->> 'creator')             :: varchar(2000) as creator,
            (audio_set ->> 'creator_url')         :: varchar(2000) as creator_url,
            (audio_set ->> 'url')                 :: varchar(1000) as url,
            (audio_set ->> 'filesize')            :: integer       as filesize,
            (audio_set ->> 'filetype')            :: varchar(80)   as filetype,
            (audio_set ->> 'thumbnail')           :: varchar(1000) as thumbnail,
			provider
		FROM audio_view
		WHERE audio_set IS NOT NULL;
	EOF"

# Load search quality assurance data.
just load-test-data "audio"
sleep 2

just load-test-data "image"
sleep 2

# Ingest and index the data
just ingest-upstream "audio" "init"
just wait-for-index "audio-init"
just promote "audio" "init" "audio"
just wait-for-index "audio"

# Image ingestion is flaky; but usally works on the next attempt
set +e
while true; do
	just ingest-upstream "image" "init"
	just wait-for-index "image-init"
	if [ $? -eq 0 ]; then
		break
	fi
	((c++)) && ((c==3)) && break
done
set -e

just promote "image" "init" "image"
just wait-for-index "image"

# Clear source cache since it's out of date after data has been loaded
docker-compose exec -T "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-image\" | redis-cli"
docker-compose exec -T "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-audio\" | redis-cli"
