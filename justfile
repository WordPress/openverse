set dotenv-load := false

DOCKER_FILE := "-f docker-compose.yml"


install:
    #! /usr/bin/env sh
    cd openverse_api
    pipenv install --dev
    pipenv run pre-commit install


lint:
    #! /usr/bin/env sh
    cd openverse_api
    pipenv run pre-commit run --all-files


env:
    #! /usr/bin/env sh
    cp openverse_api/.env.stencil openverse_api/.env
    cp ingestion_server/.env.stencil ingestion_server/.env


up:
    docker-compose {{ DOCKER_FILE }} up -d


down args="":
    docker-compose {{ DOCKER_FILE }} down {{ args }}


init: up
    ./load_sample_data.sh


healthcheck:
    curl "http://localhost:8000/v1/images/stats/"


test: up
    docker-compose exec web ./test/run_test.sh


testlocal:
    #! /usr/bin/env sh
    cd openverse_api
    pipenv run ./test/run_test.sh


logs service="":
    docker-compose {{ DOCKER_FILE }} logs -f {{ service }}


dj args="":
    #! /usr/bin/env sh
    cd openverse_api
    pipenv run python manage.py {{ args }}
