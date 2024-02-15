#!/bin/bash

# Before running the script, make sure to run the project locally following the
# instructions in the main `README.md` file.

# Fetch the schema for image and audio tables from the running DB host
docker run \
  --rm -i --network='host' --volume="$(pwd)/mock_schemas:/mock_schemas" \
  postgres \
  /bin/bash <<-EOF
		export PGPASSWORD=deploy
		pg_dump -s -t image            -U deploy -d openledger -h localhost         > /mock_schemas/image.sql
		pg_dump -s -t api_deletedimage -U deploy -d openledger -h localhost         > /mock_schemas/api_deletedimage.sql
		pg_dump -s -t api_matureimage  -U deploy -d openledger -h localhost         > /mock_schemas/api_matureimage.sql
		pg_dump -s -t audio            -U deploy -d openledger -h localhost         > /mock_schemas/audio.sql
		pg_dump -s -t api_deletedaudio -U deploy -d openledger -h localhost         > /mock_schemas/api_deletedaudio.sql
		pg_dump -s -t api_matureaudio  -U deploy -d openledger -h localhost         > /mock_schemas/api_matureaudio.sql
		pg_dump -s -t audioset         -U deploy -d openledger -h localhost         > /mock_schemas/audioset.sql
		pg_dump -s -t image_view       -U deploy -d openledger -h localhost -p 5433 > /mock_schemas/image_view.sql
		pg_dump -s -t audio_view       -U deploy -d openledger -h localhost -p 5433 > /mock_schemas/audio_view.sql
		pg_dump -s -t audioset_view    -U deploy -d openledger -h localhost -p 5433 > /mock_schemas/audioset_view.sql
		EOF

# Remove search path so we can refer to the public schema implicitly
perl -i -pe '/search_path/d' mock_schemas/image.sql
perl -i -pe '/search_path/d' mock_schemas/audio.sql
perl -i -pe '/search_path/d' mock_schemas/audioset.sql
perl -i -pe '/search_path/d' mock_schemas/image_view.sql
perl -i -pe '/search_path/d' mock_schemas/audio_view.sql
perl -i -pe '/search_path/d' mock_schemas/audioset_view.sql

# Select some media samples and export them to CSV
docker run \
  --rm --network='host' --volume="$(pwd)/mock_data:/mock_data" \
  postgres \
  /bin/bash -c "PGPASSWORD=deploy psql -U deploy -d openledger -h localhost -p 5433 <<-EOF
		\copy (SELECT * FROM image_view) to '/mock_data/mocked_image_view.csv' with (FORMAT csv, HEADER true);
		\copy (SELECT * FROM audio_view) to '/mock_data/mocked_audio_view.csv' with (FORMAT csv, HEADER true);
		EOF"

green="\e[32m"
endcol="\e[0m"
printf "%b:-) Exported new mock data${endcol}\n" "${green}"
