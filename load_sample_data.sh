#!/bin/bash
set -e
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
ANALYTICS_SERVICE_NAME="${ANALYTICS_SERVICE_NAME:-analytics}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

# Set up API database and upstream
docker-compose exec -T "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py migrate --noinput"
# Create a user for integration testing.
docker-compose exec -T "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py shell <<-EOF
	from django.contrib.auth.models import User
	user = User.objects.create_user('continuous_integration', 'test@test.test', 'deploydeploy')
	user.save()
	EOF"

# Migrate analytics
docker-compose exec -T "$ANALYTICS_SERVICE_NAME" /bin/bash -c "PYTHONPATH=. pipenv run alembic upgrade head"

# Load content providers
docker-compose exec -T "$DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);
	EOF"

docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	CREATE TABLE content_provider(provider_identifier varchar(50), provider_name varchar(250), created_on timestamp, domain_name varchar(500), filter_content boolean, notes text);
	INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);
	EOF"

# Load sample data for images
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -s -t image -U deploy -d openledger -h db | psql -U deploy -d openledger"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	ALTER TABLE image RENAME TO image_view;
	ALTER TABLE image_view ADD COLUMN standardized_popularity double precision;
	\copy image_view (id,created_on,updated_on,identifier,provider,source,foreign_identifier,foreign_landing_url,url,thumbnail,width,height,filesize,license,license_version,creator,creator_url,title,tags_list,last_synced_with_source,removed_from_source,meta_data,tags,watermarked,view_count,standardized_popularity) from './sample_data/sample_data.csv' with (FORMAT csv, HEADER true)
	EOF"

# Load sample data for audio
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -s -t audio -U deploy -d openledger -h db | head -n -14 | psql -U deploy -d openledger"
docker-compose exec -T "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	ALTER TABLE audio RENAME TO audio_view;
	ALTER TABLE audio_view ADD COLUMN standardized_popularity double precision, ADD COLUMN ingestion_type varchar(1000), ADD COLUMN audio_set jsonb, ADD COLUMN thumbnail varchar(1000);
	\copy audio_view (identifier,created_on,updated_on,ingestion_type,provider,source,foreign_identifier,foreign_landing_url,url,thumbnail,duration,bit_rate,sample_rate,category,genres,audio_set,alt_files,filesize,license,license_version,creator,creator_url,title,meta_data,tags,last_synced_with_source,removed_from_source,view_count,standardized_popularity) from './sample_data/sample_audio_data.csv' with (FORMAT csv, HEADER true)
	EOF"

# Load search quality assurance data.
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "LOAD_TEST_DATA"}'
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "audio", "action": "LOAD_TEST_DATA"}'

# Ingest and index the data
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "INGEST_UPSTREAM"}'
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "audio", "action": "INGEST_UPSTREAM"}'

# Clear source cache since it's out of date after data has been loaded
docker-compose exec -T "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-image\" | redis-cli"
