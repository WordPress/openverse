#!/bin/bash
# Set up databases
docker exec -ti cccatalog_api /bin/bash -c 'python3 manage.py makemigrations'
docker exec -ti cccatalog_api /bin/bash -c 'python3 manage.py migrate'
PGPASSWORD=deploy pg_dump -s -t image -U deploy -d openledger -h localhost -p 5432 | PGPASSWORD=deploy psql -U deploy -d openledger -p 5433 -h localhost
# Load sample data
PGPASSWORD=deploy psql -U deploy -d openledger -h localhost -p 5432 -c "INSERT INTO content_provider (created_on, provider_identifier, provider_name, domain_name, filter_content) VALUES (now(), 'flickr', 'Flickr', 'https://www.flickr.com', false);"
PGPASSWORD=deploy psql -U deploy -d openledger -h localhost -p 5433 -c "\copy image (id,created_on,updated_on,provider,source,foreign_identifier,foreign_landing_url,url,thumbnail,width,height,filesize,license,license_version,creator,creator_url,title,tags_list,last_synced_with_source,removed_from_source,meta_data,view_count,tags,watermarked,identifier) from 'sample_data.csv' with csv header"
# Ingest and index the data
curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "image", "action": "INGEST_UPSTREAM"}'
