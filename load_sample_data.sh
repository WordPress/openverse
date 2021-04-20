#!/bin/bash
set -e
CCCAPI_CONTAINER_NAME="${CCCAPI_CONTAINER_NAME:-cccatalog-api_web_1}"
ANALYTICS_CONTAINER_NAME="${ANALYTICS_CONTAINER_NAME:-cccatalog-api_analytics_1}"
# Set up API database and upstream
docker exec -i $CCCAPI_CONTAINER_NAME /bin/bash -c 'python3 manage.py migrate --noinput'
# Create a user for integration testing.
docker exec -i $CCCAPI_CONTAINER_NAME /bin/bash <<'EOF'
python3 manage.py shell -c "from django.contrib.auth.models import User
user = User.objects.create_user('continuous_integration', 'test@test.test', 'deploydeploy')
user.save()
"
EOF
# Migrate analytics
docker exec -i $ANALYTICS_CONTAINER_NAME /bin/bash -c 'PYTHONPATH=. pipenv run alembic upgrade head'
PGPASSWORD=deploy pg_dump -s -t image -U deploy -d openledger -h localhost -p 5432 | PGPASSWORD=deploy psql -U deploy -d openledger -p 5433 -h localhost
# Load sample data
PGPASSWORD=deploy psql -U deploy -d openledger -h localhost -p 5432 -c "INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);"
PGPASSWORD=deploy psql -U deploy -d openledger -h localhost -p 5433 <<EOF
ALTER TABLE image RENAME TO image_view;
ALTER TABLE image_view ADD COLUMN standardized_popularity double precision;
CREATE TABLE content_provider(provider_identifier varchar(50), provider_name varchar(250), created_on timestamp, domain_name varchar(500), filter_content boolean, notes text); INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false), (now(), 'behance', 'Behance', 'https://www.behance.net', false);
\copy image_view (id,created_on,updated_on,identifier,provider,source,foreign_identifier,foreign_landing_url,url,thumbnail,width,height,filesize,license,license_version,creator,creator_url,title,tags_list,last_synced_with_source,removed_from_source,meta_data,tags,watermarked,view_count,standardized_popularity) from './sample_data/sample_data.csv' with csv header
EOF
# Load search quality assurance data.
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "LOAD_TEST_DATA"}'
# Ingest and index the data
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "INGEST_UPSTREAM"}'
# Clear source cache since it's out of date after data has been loaded
docker exec -i cccatalog-api_cache_1 /bin/bash -c "echo \"del :1:sources-image\" | redis-cli"
