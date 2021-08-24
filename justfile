DOCKER_FILE := "openverse_catalog/docker-compose.yml"
SERVICE := "webserver"


install:
    pip install -r requirements.txt
    pre-commit install


installcatalog:
    pip install -r openverse_catalog/requirements_dev.txt


dotenv:
    @([ ! -f openverse_catalog/.env ] && cp openverse_catalog/env.template openverse_catalog/.env) || true


up: dotenv
    docker-compose --file={{ DOCKER_FILE }} up -d


down flags="":
    docker-compose --file={{ DOCKER_FILE }} down {{ flags }}


logs: dotenv
    docker-compose --file={{ DOCKER_FILE }} logs -f


test: dotenv
    docker-compose --file={{ DOCKER_FILE }} exec {{ SERVICE }} /usr/local/airflow/.local/bin/pytest


shell: dotenv
    docker-compose --file={{ DOCKER_FILE }} exec {{ SERVICE }} /bin/bash


airflow command: dotenv
    docker-compose --file={{ DOCKER_FILE }} exec {{ SERVICE }} airflow {{ command }}
