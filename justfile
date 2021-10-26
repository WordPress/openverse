set dotenv-load := false

# Show all available recipes
default:
  @just --list --unsorted

IS_PROD := env_var_or_default("IS_PROD", "")
DOCKER_FILES := "--file=docker-compose.yml" + (
    if IS_PROD != "true" {" --file=docker-compose.override.yml"} else {""}
)
SERVICE := "webserver"


# Install dependencies into the current environment
install:
    pip install -r requirements.txt -r requirements_dev.txt
    pre-commit install

# Create the .env file from the template
dotenv:
    @([ ! -f .env ] && cp env.template .env) || true

# Build all (or specified) container(s)
build service="": dotenv
    docker-compose {{ DOCKER_FILES }} build {{ service }}

# Bring all Docker services up
up flags="": dotenv
    docker-compose {{ DOCKER_FILES }} up -d {{ flags }}

# Take all Docker services down
down flags="":
    docker-compose {{ DOCKER_FILES }} down {{ flags }}

# Recreate all volumes and containers from scratch
recreate: dotenv
    @just down -v
    @just up "--force-recreate --build"

# Show logs of all, or named, Docker services
logs service="": up
    docker-compose {{ DOCKER_FILES }} logs -f {{ service }}

# Pull, build, and deploy all services
deploy:
    @just down
    -git pull
    @just build
    @just up

# Run pre-commit on all files
lint:
    pre-commit run --all-files

# Mount the tests directory and run a particular command
@_mount-tests command: (up "postgres s3")
    # The test directory is mounted into the container only during testing
    docker-compose {{ DOCKER_FILES }} run \
        -v {{ justfile_directory() }}/tests:/usr/local/airflow/tests/ \
        --rm \
        {{ SERVICE }} \
        {{ command }}

# Run a container that can be used for repeated interactive testing
test-session:
    @just _mount-tests bash

# Run pytest using the webserver image
test pytestargs="":
    @just _mount-tests /usr/local/airflow/.local/bin/pytest {{ pytestargs }}

# Open a shell into the webserver container
shell: up
    docker-compose {{ DOCKER_FILES }} exec {{ SERVICE }} /bin/bash

# Launch an IPython REPL within the webserver container
ipython: up
    docker-compose {{ DOCKER_FILES }} exec -w /usr/local/airflow/openverse_catalog/dags {{ SERVICE }} /usr/local/airflow/.local/bin/ipython

# Run a given airflow command using the webserver image
airflow command="": up
    docker-compose {{ DOCKER_FILES }} exec {{ SERVICE }} airflow {{ command }}

# Launch a pgcli shell on the postgres container (defaults to openledger) use "airflow" for airflow metastore
db-shell args="openledger": up
    docker-compose {{ DOCKER_FILES }} exec postgres pgcli {{ args }}
