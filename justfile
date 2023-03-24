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
    cd docker/nginx && just
    cd docker/es && just
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

# Installs Node.js dependencies for the entire monorepo.
node-install:
    pnpm i
    just frontend/run i18n:en
    just frontend/run i18n:copy-test-locales

# Install all dependencies
install: node-install
    just automations/python/install
    just documentation/install

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
env:
    cp api/env.template api/.env
    cp ingestion_server/env.template ingestion_server/.env

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
    env COMPOSE_PROFILES="{{ env_var_or_default("COMPOSE_PROFILES", "api,ingestion_server,frontend") }}" docker-compose {{ DOCKER_FILE }} {{ args }}

# Build all (or specified) services
build *args:
    just dc build {{ args }}

# Also see `up` recipe in sub-justfiles
# Bring all Docker services up, in all profiles
up *flags:
    just dc up -d {{ flags }}

# Also see `wait-up` recipe in sub-justfiles
# Wait for all services to be up
wait-up: up
    just ingestion_server/wait-up
    just api/wait-up
    just frontend/wait-up

# Also see `init` recipe in sub-justfiles
# Load sample data into the Docker Compose services
init:
    just api/init
    just frontend/init

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

# Attach to the specificed `service`. Enables interacting with the TTY of the running service.
attach service:
    docker attach $(docker-compose ps | grep {{ service }} | awk '{print $1}')

EXEC_DEFAULTS := if IS_CI == "" { "" } else { "-T" }

# Execute statement in service containers using Docker Compose
exec +args:
    just dc exec -u {{ DC_USER }} {{ EXEC_DEFAULTS }} {{ args }}
