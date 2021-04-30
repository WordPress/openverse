#!/bin/bash
set -e
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
ANALYTICS_SERVICE_NAME="${ANALYTICS_SERVICE_NAME:-analytics}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

# Set up API database and upstream
docker-compose exec "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py migrate --noinput"
# Create a user for integration testing.
docker-compose exec "$WEB_SERVICE_NAME" /bin/bash -c "python3 manage.py shell <<-EOF
	from django.contrib.auth.models import User
	user = User.objects.create_user('continuous_integration', 'test@test.test', 'deploydeploy')
	user.save()
	EOF"

# Migrate analytics
docker-compose exec "$ANALYTICS_SERVICE_NAME" /bin/bash -c "PYTHONPATH=. pipenv run alembic upgrade head"
# Copy table `image` from database to upstream database
docker-compose exec "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "PGPASSWORD=deploy pg_dump -s -t image -U deploy -d openledger -h db | psql -U deploy -d openledger"
# Load content providers
docker-compose exec "$DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);
	EOF"
# Load sample data, including content providers
docker-compose exec "$UPSTREAM_DB_SERVICE_NAME" /bin/bash -c "psql -U deploy -d openledger <<-EOF
	ALTER TABLE image RENAME TO image_view;
	ALTER TABLE image_view ADD COLUMN standardized_popularity double precision;
	CREATE TABLE content_provider(provider_identifier varchar(50), provider_name varchar(250), created_on timestamp, domain_name varchar(500), filter_content boolean, notes text);
	INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);
	\copy image_view (id,created_on,updated_on,identifier,provider,source,foreign_identifier,foreign_landing_url,url,thumbnail,width,height,filesize,license,license_version,creator,creator_url,title,tags_list,last_synced_with_source,removed_from_source,meta_data,tags,watermarked,view_count,standardized_popularity) from './sample_data/sample_data.csv' with csv header
	EOF"

# Load search quality assurance data.
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "LOAD_TEST_DATA"}'
# Ingest and index the data
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "INGEST_UPSTREAM"}'

# Clear source cache since it's out of date after data has been loaded
docker-compose exec "$CACHE_SERVICE_NAME" /bin/bash -c "echo \"del :1:sources-image\" | redis-cli"
