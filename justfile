set dotenv-load := false

# Meaning of Just prefixes:
# @ - Quiet recipes (https://github.com/casey/just#quiet-recipes)
# _ - Private recipes (https://github.com/casey/just#private-recipes)

IS_PROD := env_var_or_default("PROD", "")
IS_CI := env_var_or_default("CI", "")
DC_USER := env_var_or_default("DC_USER", "opener")

# Show all available recipes, also recurses inside nested justfiles
@_default:
    just --list --unsorted
    cd nginx && just
    cd api && just
    cd ingestion_server && just
    cd frontend && just
    cd automations/python && just
    cd automations/js && just
    cd documentation && just
    printf "\nTo run a nested recipe, add the folder path before it, like \`just frontend/install\`.\n"

###########
# Helpers #
###########

# Sleep for given time showing the given message as long as given condition is met
@_loop condition message timeout="5m" time="5":
    timeout --foreground {{ timeout }} bash -c 'while [ {{ condition }} ]; do \
      echo "{{ message }}" && sleep {{ time }}; \
    done'; \
    EXIT_CODE=$?; \
    if [ $EXIT_CODE -eq 124 ]; then \
      echo "Timed out"; \
      exit $EXIT_CODE; \
    fi

#######
# Dev #
#######

# Install all dependencies
@install:
    just frontend/install
    just automations/python/install
    just automations/js/install
    just documentation/install

# Setup pre-commit as a Git hook
precommit:
    #!/usr/bin/env bash
    set -eo pipefail
    if [ -z "$SKIP_PRE_COMMIT" ] && [ ! -f ./pre-commit.pyz ]; then
      echo "Downloading pre-commit"
      URL=$(
        curl \
          --fail \
          --silent `# silence error raised by grep closing the pipe early` \
          ${GITHUB_TOKEN:+ --header "Authorization: Bearer ${GITHUB_TOKEN}"} \
          https://api.github.com/repos/pre-commit/pre-commit/releases/latest |
          grep -o 'https://.*\.pyz' -m 1
      )
      echo "Download URL: $URL"
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
env:
    cp api/env.template api/.env
    cp ingestion_server/env.template ingestion_server/.env

# Ensure all services are up and running
@_all-up:
    just up
    just ingestion_server/wait
    just api/wait

# Load sample data into the Docker Compose services
init: _all-up
    ./load_sample_data.sh

##########
# Docker #
##########

DOCKER_FILE := "-f " + (
    if IS_PROD == "true" { "ingestion_server/docker-compose.yml" }
    else { "docker-compose.yml" }
)

# Run `docker-compose` configured with the correct files and environment
dc *args:
    @{{ if IS_CI != "" { "just env" } else { "true" } }}
    docker-compose {{ DOCKER_FILE }} {{ args }}

# Build all (or specified) services
build *args:
    just dc build {{ args }}

# Bring all Docker services up
up *flags="":
    just dc up -d {{ flags }}

# Take all Docker services down
down flags="":
    just dc down {{ flags }}

# Recreate all volumes and containers from scratch
recreate:
    just down -v
    just up "--force-recreate --build"
    just init

# Show logs of all, or named, Docker services
logs services="" args=(if IS_CI != "" { "" } else { "-f" }):
    just dc logs {{ args }} {{ services }}

# Attach to the specificed `service`. Enables interacting with the TTY of the running service.
attach service:
    docker attach $(docker-compose ps | grep {{ service }} | awk '{print $1}')

EXEC_DEFAULTS := if IS_CI == "" { "" } else { "-T" }

# Execute statement in service containers using Docker Compose
exec +args:
    just dc exec -u {{ DC_USER }} {{ EXEC_DEFAULTS }} {{ args }}

#################
# Elasticsearch #
#################

# Check the health of Elasticsearch
@es-health es_host:
    -curl -s -o /dev/null -w '%{http_code}' 'http://{{ es_host }}/_cluster/health'

# Wait for Elasticsearch to be healthy
@wait-for-es es_host="localhost:50292":
    just _loop \
    '"$(just es-health {{ es_host }})" != "200"' \
    "Waiting for Elasticsearch to be healthy..."

@check-index index="image":
    -curl -sb -H "Accept:application/json" "http://localhost:50292/_cat/indices/{{ index }}" | grep -o "{{ index }}" | wc -l | xargs

# Wait for the media to be indexed in Elasticsearch
@wait-for-index index="image":
    just _loop \
    '"$(just check-index {{ index }})" != "1"' \
    "Waiting for index '{{ index }}' to be ready..."
