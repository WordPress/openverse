set dotenv-load := false

# Meaning of Just prefixes:
# @ - Quiet recipes (https://github.com/casey/just#quiet-recipes)
# _ - Private recipes (https://github.com/casey/just#private-recipes)

# The monorepo uses `PROD` instead of `IS_PROD`.
IS_PROD := env_var_or_default("IS_PROD", "")
IS_CI := env_var_or_default("CI", "")

# Show all available recipes
@_default:
  just --list --unsorted
  cd catalog/ && just

#######
# Dev #
#######

# Setup pre-commit as a Git hook
precommit:
    #!/usr/bin/env bash
    set -eo pipefail
    if [ -z "$SKIP_PRE_COMMIT" ] && [ ! -f ./pre-commit.pyz ]; then
      echo "Getting latest release"
      curl \
        ${GITHUB_TOKEN:+ --header "Authorization: Bearer ${GITHUB_TOKEN}"} \
        --output latest.json \
        https://api.github.com/repos/pre-commit/pre-commit/releases/latest
      cat latest.json
      URL=$(grep -o 'https://.*\.pyz' -m 1 latest.json)
      rm latest.json
      echo "Downloading pre-commit from $URL"
      curl \
        --fail \
        --location `# follow redirects, else cURL outputs a blank file` \
        --output pre-commit.pyz \
        ${GITHUB_TOKEN:+ --header "Authorization: Bearer ${GITHUB_TOKEN}"} \
        "$URL"
      echo "Installing pre-commit"
      python3 pre-commit.pyz install -t pre-push -t pre-commit
      echo "Done"
    else
      echo "Skipping pre-commit installation"
    fi

# Run pre-commit to lint and reformat files
lint hook="" *files="": precommit
    python3 pre-commit.pyz run {{ hook }} {{ if files == "" { "--all-files" } else { "--files" } }}  {{ files }}

########
# Init #
########

# Create .env files from templates
@env:
    # Root
    ([ ! -f .env ] && cp env.template .env) || true
    # Docker
    ([ ! -f docker/local_postgres/.env ] && cp docker/local_postgres/env.template docker/local_postgres/.env) || true
    ([ ! -f docker/minio/.env ] && cp docker/minio/env.template docker/minio/.env) || true
    # First party services
    ([ ! -f catalog/.env ] && cp catalog/env.template catalog/.env) || true

##########
# Docker #
##########

DOCKER_FILE := "-f " + (
    if IS_PROD == "true" { "catalog/docker-compose.yml" }
    else { "docker-compose.yml" }
)
EXEC_DEFAULTS := if IS_CI == "" { "" } else { "-T" }
DC_USER := env_var_or_default("DC_USER", "airflow")

export PROJECT_PY_VERSION := `just catalog/py-version`
export PROJECT_AIRFLOW_VERSION := `just catalog/airflow-version`

# Run `docker-compose` configured with the correct files and environment
dc *args:
    @{{ if IS_CI != "" { "just env" } else { "true" } }}
    env COMPOSE_PROFILES="{{ env_var_or_default("COMPOSE_PROFILES", "api,ingestion_server,frontend,catalog") }}" docker-compose {{ DOCKER_FILE }} {{ args }}

# Build all (or specified) services
build *args:
    just dc build {{ args }}

# Also see `up` recipe in sub-justfiles
# Bring all Docker services up, in all profiles
up *flags:
    #!/usr/bin/env bash
    set -eo pipefail
    while true; do
      if just dc up -d {{ flags }} ; then
        break
      fi
      ((c++)) && ((c==3)) && break
      sleep 5
    done

# Also see `wait-up` recipe in sub-justfiles
# Wait for all services to be up
wait-up: up
    just catalog/wait-up

# Also see `init` recipe in sub-justfiles
# Load sample data into the Docker Compose services
init:
    echo "🚧 TODO"

# Take all Docker services down, in all profiles
down *flags:
    just dc down {{ flags }}

# Recreate all volumes and containers from scratch
recreate:
    just down -v
    just up "--force-recreate --build"
    just init

# Show logs of all, or named, Docker services
logs services="" args=(if IS_CI != "" { "" } else { "-f" }):
    just dc logs {{ args }} {{ services }}

# Attach to the specificed `service` with interactive TTY
attach service:
    docker attach $(docker-compose ps | grep {{ service }} | awk '{print $1}')

# Execute statement in service containers using Docker Compose
exec +args:
    just dc exec -u {{ DC_USER }} {{ EXEC_DEFAULTS }} {{ args }}

# Execute statement in a new service container using Docker Compose
run +args:
    just dc run -u {{ DC_USER }} {{ EXEC_DEFAULTS }} "{{ args }}"

########
# Misc #
########

# Pull, build, and deploy all services
deploy:
    -git pull
    @just pull
    @just up
