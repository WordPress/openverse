#!/bin/bash

# Fetches mock data from a running postgres database.

export PGPASSWORD="deploy"
# Dump schema
pg_dump -s -h localhost -U deploy -d openledger -t 'image' > schema.sql
# Remove search path (so we can refer to the public schema implicitly)
sed -ie '/search_path/d' schema.sql
# Select some images and save to CSV
psql -h localhost -U deploy -d openledger -c "\\copy (select * from image where meta_data is not null limit 1000) to './mocked_images.csv' with CSV"
exit 0
