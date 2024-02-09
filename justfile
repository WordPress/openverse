set dotenv-load := false

# Meaning of Just prefixes:
# @ - Quiet recipes (https://github.com/casey/just#quiet-recipes)
# _ - Private recipes (https://github.com/casey/just#private-recipes)

IS_PROD := env_var_or_default("PROD", env_var_or_default("IS_PROD", ""))
# `PROD_ENV` can be "ingestion_server" or "catalog"
PROD_ENV := env_var_or_default("PROD_ENV", "")
IS_CI := env_var_or_default("CI", "")
DC_USER := env_var_or_default("DC_USER", "opener")

# Show all available recipes, also recurses inside nested justfiles
@_default:
    just --list --unsorted
    cd docker/cache && just
    cd docker/nginx && just
    cd docker/es && just
    cd catalog && just
    cd api && just
    cd ingestion_server && just
    cd frontend && just
    cd automations/python && just
    cd automations/js && just
    cd documentation && just
    cd .vale && just
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

# Install Node.js dependencies for the entire monorepo
node-install:
    pnpm i
    just frontend/run i18n:en
    just frontend/run i18n:copy-test-locales

# Install Python dependences for the monorepo
py-install:
    just automations/python/install
    just documentation/install

# Install all dependencies
install:
    just node-install
    just py-install

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

# Run codeowners validator locally. Only enable experimental hooks if there are no uncommitted changes.
lint-codeowners checks="stable":
    docker run --rm \
        -u 1000:1000 \
        -v $PWD:/src:rw,Z \
        --workdir=/src \
        -e REPOSITORY_PATH="." \
        -e CHECKS="files,duppaterns,syntax" \
        {{ if checks != "stable" { "-e EXPERIMENTAL_CHECKS='notowned,avoid-shadowing'" } else { "" } }} \
        ghcr.io/mszostok/codeowners-validator:v0.7.4

########
# Init #
########

# Create .env files from templates
@env:
    # Root
    ([ ! -f .env ] && cp env.template .env) || true
    # Docker
    ([ ! -f docker/minio/.env ] && cp docker/minio/env.template docker/minio/.env) || true
    # First-party services
    ([ ! -f catalog/.env ] && cp catalog/env.template catalog/.env) || true
    ([ ! -f ingestion_server/.env ] && cp ingestion_server/env.template ingestion_server/.env) || true
    ([ ! -f api/.env ] && cp api/env.template api/.env) || true

##########
# Docker #
##########

DOCKER_FILE := "-f " + (
    if IS_PROD == "true" {
        if PROD_ENV == "ingestion_server" { "ingestion_server/docker-compose.yml" }
        else if PROD_ENV == "catalog" { "catalog/docker-compose.yml" }
        else { "docker-compose.yml" }
    }
    else { "docker-compose.yml" }
)
EXEC_DEFAULTS := if IS_CI == "" { "" } else { "-T" }

export CATALOG_PY_VERSION := `just catalog/py-version`
export CATALOG_AIRFLOW_VERSION := `just catalog/airflow-version`
export API_PY_VERSION := `just api/py-version`
export INGESTION_PY_VERSION := `just ingestion_server/py-version`
export FRONTEND_NODE_VERSION := `just frontend/node-version`
export FRONTEND_PNPM_VERSION := `just frontend/pnpm-version`
export PGCLI_VERSION := `just api/pgcli-version`

export HOST_NETWORK_ADDRESS := if os() == "macos" { "host.docker.internal" } else { "172.17.0.1" }

versions:
    #!/usr/bin/env bash
    cat <<EOF
    catalog_py_version=$(just catalog/py-version)
    catalog_airflow_version=$(just catalog/airflow-version)
    api_py_version=$(just api/py-version)
    ingestion_py_version=$(just ingestion_server/py-version)
    frontend_node_version=$(just frontend/node-version)
    frontend_pnpm_version=$(just frontend/pnpm-version)
    pgcli_version=$(just api/pgcli-version)
    EOF

# Run `docker-compose` configured with the correct files and environment
dc *args:
    @{{ if IS_CI != "" { "just env" } else { "true" } }}
    env COMPOSE_PROFILES="{{ env_var_or_default("COMPOSE_PROFILES", "api,ingestion_server,frontend,catalog") }}" docker-compose {{ DOCKER_FILE }} {{ args }}

# Build all (or specified) services
build *args:
    just dc build {{ args }}

# List all services and their URLs and ports
@ps:
    # ps is a helper command & intermediate dependency, so it should not fail the whole
    # command if it fails
    python3 utilities/ps.py || true

# Also see `up` recipe in sub-justfiles
# Bring all Docker services up, in all profiles
up *flags: env && ps
    #!/usr/bin/env bash
    set -eo pipefail
    while true; do
      if just dc up -d {{ flags }} ; then
        break
      fi
      ((c++)) && ((c==3)) && break
      sleep 5
    done
    echo && sleep 1

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

# Bust pnpm cache and reinstall Node.js dependencies
node-recreate:
    find . -name 'node_modules' -type d -prune -exec rm -rf '{}' +
    rm -rf $(pnpm store path)
    pnpm install

# Show logs of all, or named, Docker services
logs services="" args=(if IS_CI != "" { "" } else { "-f" }):
    just dc logs {{ args }} {{ services }}

# Attach to the specified service to interacting with its TTY
attach service:
    docker attach $(just dc ps | awk '{print $1}' | grep {{ service }})

# Execute statement in service containers using Docker Compose
exec +args:
    just dc exec -u {{ env_var_or_default("DC_USER", "root") }} {{ EXEC_DEFAULTS }} {{ args }}

# Execute statement in a new service container using Docker Compose
run +args:
    just dc run -u {{ env_var_or_default("DC_USER", "root") }} {{ EXEC_DEFAULTS }} "{{ args }}"

# Execute pgcli against one of the database instances
_pgcli container db_user_pass db_name db_host db_port="5432":
    just exec {{ container }} pgcli postgresql://{{ db_user_pass }}:{{ db_user_pass }}@{{ db_host }}:{{ db_port }}/{{ db_name }}

########
# Misc #
########

# Pull, build, and deploy all services
deploy:
    -git pull
    @just pull
    @just up

#####################
# Aliases/shortcuts #
#####################

alias b := build
alias d := down
alias l := lint

alias L := logs
alias P := precommit
alias I := install

# alias for `just api/up`
a:
    just api/up

# alias for `just catalog/up`
c:
    just catalog/up

# alias for `just documentation/live`, 's' for Sphinx
s:
    just documentation/live

# alias for `just ingestion_server/up`
i:
    just ingestion_server/up

# alias for `just frontend/run dev`
f:
    just frontend/run dev

# alias for `pnpm --filter {package} run {script}`
p package script +args="":
    pnpm --filter {{ package }} run {{ script }} {{ args }}
