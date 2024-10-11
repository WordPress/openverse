#! /usr/bin/env bash
set -e
set -o pipefail
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-web}"
CACHE_SERVICE_NAME="${CACHE_SERVICE_NAME:-cache}"
UPSTREAM_DB_SERVICE_NAME="${UPSTREAM_DB_SERVICE_NAME:-upstream_db}"
DB_SERVICE_NAME="${DB_SERVICE_NAME:-db}"

# Detect whether the `AIRFLOW_CONN_SENSITIVE_TERMS` is set
# `true` resolves to an empty string, and prevents the script from failing
# due to `set -e` and grep's non-zero status code if the pattern isn't found
has_sensitive_terms_airflow_conn=$(grep "AIRFLOW_CONN_SENSITIVE_TERMS" catalog/.env || true)

# Temporary measure to prevent errors in the data refresh portion of the script
# when the AIRFLOW_CONN_SENSITIVE_TERMS is not defined in the .env file, by
# detecting when the variable is missing and populating it with the default from
# the template. This is only necessary temporarily, pending the work to undo the
# split indices for sensitive text detection
# (https://github.com/WordPress/openverse/pull/4904/files)
if [[ ! $has_sensitive_terms_airflow_conn ]]; then
  echo "Adding new Airflow connection environment variable required for sample data loading"
  grep "AIRFLOW_CONN_SENSITIVE_TERMS" catalog/env.template >>catalog/.env

  echo "Restarting Airflow to populate the new connection variable"
  just dc restart webserver scheduler triggerer
fi

while getopts 'c' OPTION; do
  case "$OPTION" in
  c)
    echo "Loading upstream DB data..."
    upstream_only=true
    ;;
  ?)
    echo "Loading all sample data..."
    ;;
  esac
done

###############
# Upstream DB #
###############

function exec_sql {
  echo "$2" | just dc exec -T "$1" psql -AXqt
}

# Load sample data
function load_sample_data {
  exec_sql "$UPSTREAM_DB_SERVICE_NAME" "
  	DELETE FROM $1;
	\copy $1 \
		from './sample_data/sample_$1.csv' \
		with (FORMAT csv, HEADER true);
"
}

function verify_loaded_data {
  COUNT=$(exec_sql "$UPSTREAM_DB_SERVICE_NAME" "SELECT COUNT(*) FROM $1;")
  if [ "$COUNT" -ne 5000 ]; then
    echo "Error: table $1 count differs from expected."
    exit 1
  fi
}

load_sample_data "image"
verify_loaded_data "image"
load_sample_data "audio"
verify_loaded_data "audio"

# Terminate the script if received flag for only upstream data
if [ "$upstream_only" = true ]; then
  exit 0
fi

#######
# API #
#######

# Set up API database and upstream
just dc exec -T "$WEB_SERVICE_NAME" python3 manage.py migrate --noinput

# Create a superuser and a user for integration testing
echo "
from django.contrib.auth.models import User
usernames = ['continuous_integration', 'deploy', 'moderator']
for username in usernames:
  if User.objects.filter(username=username).exists():
    print(f'User {username} already exists')
    continue
  if username == 'deploy':
    user = User.objects.create_superuser(username, f'{username}@example.com', 'deploy')
  else:
    is_staff = username == 'moderator'
    user = User.objects.create_user(username, f'{username}@example.com', 'deploy', is_staff=is_staff)
  user.save()
" | just dc exec -T "$WEB_SERVICE_NAME" python3 manage.py shell

# Create the Content Moderator group and add the moderator to it
# Credit: https://stackoverflow.com/a/53733693
echo "
from django.contrib.auth.models import User, Group, Permission
crud_perm_map = {'C': 'add', 'R': 'view', 'U': 'change', 'D': 'delete'}
model_perms_map = {
  'audio': 'R',
  'deletedaudio': 'R',
  'sensitiveaudio': 'R',
  'audioreport': 'R',
  'audiodecision': 'CR',
  'audiodecisionthrough': 'R',
  'image': 'R',
  'deletedimage': 'R',
  'sensitiveimage': 'R',
  'imagereport': 'R',
  'imagedecision': 'CR',
  'imagedecisionthrough': 'R',
}
mod_group, created = Group.objects.get_or_create(name='Content Moderators')
if created:
  print('Setting up Content Moderators group')
  for model, perms in model_perms_map.items():
    for perm in perms:
      name = f'{crud_perm_map[perm]}_{model}'
      print(f'Adding permission to moderators group: {name}')
      model_add_perm = Permission.objects.get(codename=name)
      mod_group.permissions.add(model_add_perm)
  mod_group.save()
  mod_group.user_set.add(User.objects.get(username='moderator'))
" | just dc exec -T "$WEB_SERVICE_NAME" python3 manage.py shell

# Load content providers
exec_sql "$DB_SERVICE_NAME" "
DELETE FROM content_provider;
INSERT INTO content_provider
	(created_on, provider_identifier, provider_name, domain_name, filter_content, media_type)
VALUES
	(now(), 'flickr', 'Flickr', 'https://www.flickr.com', false, 'image'),
	(now(), 'stocksnap', 'StockSnap', 'https://stocksnap.io', false, 'image'),
	(now(), 'freesound', 'Freesound', 'https://freesound.org/', false, 'audio'),
	(now(), 'jamendo', 'Jamendo', 'https://www.jamendo.com', false, 'audio'),
	(now(), 'wikimedia_audio', 'Wikimedia', 'https://commons.wikimedia.org', false, 'audio'),
	(now(), 'ccmixter', 'CCMixter', 'https://ccmixter.org', false, 'audio');
"

#############
# Ingestion #
#############

# Remove base indices if they exist
just docker/es/delete-index audio-init
just docker/es/delete-index audio-init-filtered
just docker/es/delete-index image-init
just docker/es/delete-index image-init-filtered

# Ingest and index the data
# Enable the staging data refresh dags, if they are not already.
# These DAGs are on a None schedule so no scheduled runs will be
# triggered.
just catalog/cli airflow dags unpause staging_audio_data_refresh
just catalog/cli airflow dags unpause staging_image_data_refresh
# Trigger the data refresh dags at the same time. The DAGs will manage
# concurrency issues.
just catalog/cli airflow dags trigger staging_audio_data_refresh --conf '{"index_suffix": "init", "allow_concurrent_data_refreshes": true}'
just catalog/cli airflow dags trigger staging_image_data_refresh --conf '{"index_suffix": "init", "allow_concurrent_data_refreshes": true}'
# Wait for all relevant indices to be created and promoted
just docker/es/wait-for-index "audio"
just docker/es/wait-for-count "audio"
just docker/es/wait-for-index "audio-filtered" "audio-init-filtered"
just docker/es/wait-for-index "image"
just docker/es/wait-for-count "image"
just docker/es/wait-for-index "image-filtered" "image-init-filtered"

#########
# Redis #
#########

# Clear source cache since it's out of date after data has been loaded
function exec_redis {
  echo "$1" | just dc exec -T "$CACHE_SERVICE_NAME" redis-cli
}
exec_redis "del :1:sources-image"
exec_redis "del :1:sources-audio"
