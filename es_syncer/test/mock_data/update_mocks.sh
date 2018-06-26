#!/bin/bash

# Fetches mock data from a running postgres database.

export PGPASSWORD="deploy"
pg_dump -s -h localhost -U deploy -d openledger -t 'image' > schema.sql
psql -h localhost -U deploy -d openledger -c "\\copy (select * from image where meta_data is not null limit 1000) to './mocked_images.csv' with CSV"
exit 0
