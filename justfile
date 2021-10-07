set dotenv-load := false

# Show all available recipes
default:
  @just --list --unsorted


###########
# Helpers #
###########

# Sleep for given time showing the given message as long as given condition is met
@_loop condition message time="1":
    while [[ {{ condition }} ]]; do \
        echo "{{ message }}" && sleep {{ time }}; \
    done


##########
# Docker #
##########

DOCKER_FILE := "-f docker-compose.yml"

# Bring all Docker services up
up:
    docker-compose {{ DOCKER_FILE }} up -d

# Take all Docker services down
down args="":
    docker-compose {{ DOCKER_FILE }} down {{ args }}

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

@es-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:9200/_cluster/health?pretty'

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

# Check the health of the ingestion-server
@is-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8001/'

# Wait for the health of the ingestion-server
@wait-for-is: up
    just _loop \
    '"$(just is-health)" != "200"' \
    "Waiting for the ingestion-server to be healthy..."

# Load QA data into QA indices in Elasticsearch
load-test-data model="image":
    curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "{{ model }}", "action": "LOAD_TEST_DATA"}'

# Load sample data into prod indices in Elasticsearch
ingest-upstream model="image":
    curl -XPOST localhost:8001/task -H "Content-Type: application/json" -d '{"model": "{{ model }}", "action": "INGEST_UPSTREAM"}'


#######
# API #
#######

# Check the health of the API
@web-health:
    -curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8000/healthcheck'

# Wait for the health of the API
@wait-for-web: up
    just _loop \
    '"$(just web-health)" != "200"' \
    "Waiting for the API to be healthy..."

# Run API tests inside Docker
test: wait-for-es wait-for-is wait-for-web
    docker-compose exec web ./test/run_test.sh

# Run API tests locally
testlocal:
    cd openverse_api && pipenv run ./test/run_test.sh

# Run Django administrative commands
dj args="":
    cd openverse_api && pipenv run python manage.py {{ args }}

# Make a test cURL request to the API
stats media="images":
    curl "http://localhost:8000/v1/{{ media }}/stats/"
