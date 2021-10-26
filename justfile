set dotenv-load := false

# Show all available recipes
default:
  @just --list --unsorted


###########
# Helpers #
###########

# Sleep for given time showing the given message as long as given condition is met
@_loop condition message time="5":
    while [ {{ condition }} ]; do \
        echo "{{ message }}" && sleep {{ time }}; \
    done


##########
# Docker #
##########

DOCKER_FILE := "-f docker-compose.yml"

# Bring all Docker services up
up flags="":
    docker-compose {{ DOCKER_FILE }} up -d {{ flags }}

# Take all Docker services down
down flags="":
    docker-compose {{ DOCKER_FILE }} down {{ flags }}

# Recreate all volumes and containers from scratch
recreate:
    @just down -v
    @just up "--force-recreate --build"

# Show logs of all, or named, Docker services
logs services="":
    docker-compose {{ DOCKER_FILE }} logs -f {{ services }}


########
# Init #
########

# Create .env files from templates
env:
    cp openverse_api/env.template openverse_api/.env
    cp ingestion_server/env.template ingestion_server/.env

# Load sample data into the Docker Compose services
init: wait-for-es wait-for-is wait-for-web
    ./load_sample_data.sh


#######
# Dev #
#######

# Install Python dependencies in Pipenv environments
install:
    cd openverse_api && pipenv install --dev
    cd ingestion_server && pipenv install --dev

# Setup pre-commit as a Git hook
precommit:
    cd openverse_api && pipenv run pre-commit install

# Run pre-commit to lint and reformat all files
lint:
    cd openverse_api && pipenv run pre-commit run --all-files


#################
# Elasticsearch #
#################

# Check the health of Elasticsearch
@es-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:9200/_cluster/health?pretty'

# Wait for Elasticsearch to be healthy
@wait-for-es: up
    just _loop \
    '"$(just es-health)" != "200"' \
    "Waiting for Elasticsearch to be healthy..."

# Check if the media is indexed in Elasticsearch
@check-index index="image":
    -curl -sb -H "Accept:application/json" "http://localhost:9200/_cat/aliases/{{ index }}" | grep -c "{{ index }}-"

# Wait for the media to be indexed in Elasticsearch
@wait-for-index index="image":
    just _loop \
    '"$(just check-index {{ index }})" != "1"' \
    "Waiting for index '{{ index }}' to be ready..."


####################
# Ingestion server #
####################

# Perform the given action on the given model by invoking the ingestion-server API
_is-api model action:
    curl \
      -X POST \
      -H 'Content-Type: application/json' \
      -d '{"model": "{{ model }}", "action": "{{ action }}"}' \
      'http://localhost:8001/task'

# Check the health of the ingestion-server
@is-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8001/'

# Wait for the ingestion-server to be healthy
@wait-for-is: up
    just _loop \
    '"$(just is-health)" != "200"' \
    "Waiting for the ingestion-server to be healthy..."

# Load QA data into QA indices in Elasticsearch
load-test-data model="image":
    just _is-api {{ model }} "LOAD_TEST_DATA"

# Load sample data into prod indices in Elasticsearch
ingest-upstream model="image":
    just _is-api {{ model }} "INGEST_UPSTREAM"


#######
# API #
#######

# Check the health of the API
@web-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8000/healthcheck'

# Wait for the API to be healthy
@wait-for-web: up
    just _loop \
    '"$(just web-health)" != "200"' \
    "Waiting for the API to be healthy..."

# Run API tests inside Docker
test args="": wait-for-es wait-for-is wait-for-web
    docker-compose exec {{ args }} web ./test/run_test.sh

# Run API tests locally
testlocal:
    cd openverse_api && pipenv run ./test/run_test.sh

# Run Django administrative commands
dj args="":
    cd openverse_api && pipenv run python manage.py {{ args }}

# Make a test cURL request to the API
stats media="images":
    curl "http://localhost:8000/v1/{{ media }}/stats/"


#############
# Analytics #
#############

nl-test args="":
    docker-compose exec {{ args }} analytics pytest tests.py
