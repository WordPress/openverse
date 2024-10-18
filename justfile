set dotenv-load := false

# Meaning of Just prefixes:
# @ - Quiet recipes (https://github.com/casey/just#quiet-recipes)
# _ - Private recipes (https://github.com/casey/just#private-recipes)

IS_CI := env_var_or_default("CI", "")
DC_USER := env_var_or_default("DC_USER", "opener")

# Show all available recipes, also recurses inside nested justfiles
@_default:
    just --list --unsorted
    cd packages/python/openverse-attribution && just
    cd docker/cache && just
    cd docker/es && just
    cd catalog && just
    cd api && just
    cd ingestion_server && just
    cd indexer_worker && just
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
    pnpm --filter './packages/js/*' run build
    pnpm prepare:nuxt
    just frontend/run i18n:en


# Set up locales for the frontend
locales mode="test":
    #! /usr/bin/env bash
    if [ "{{ mode }}" = "production" ]; then
        just frontend/run i18n
    elif [ "{{ mode }}" = "test" ]; then
        just frontend/run i18n:copy-test-locales
    else
        echo "Invalid mode {{ mode }}. Using only the `en` locale. To set up more locales, use 'production' or 'test'."
    fi

# Install Python dependences for the monorepo
py-install:
    just automations/python/install
    just documentation/install

# Install all dependencies
install:
    just node-install
    just py-install

# Install `ov`-based git hooks
@install-hooks:
    bash -c "cp ./docker/dev_env/hooks/* ./.git/hooks"
    # Run pnpm install to ensure eslint and prettier are available
    pnpm install

# Create an `.ov_profile.json` as a starting point for development environment customisation. Does not make changes if the file already exists.
init-ov-profile:
    #! /usr/bin/env bash
    [[ -f ./.ov_profile.json ]] && echo '.ov_profile.json already exists! No changes made.' && exit 0 || cat <<-'EOALIASES' > ./.ov_profile.json
    {
      "aliases": {
        "welcome": {
          "cmd": ["just", "welcome-to-openverse"],
          "doc": "Warmly welcome Openverse contributors (and provide an example for how aliases work)."
        }
      }
    }
    EOALIASES

# Recipe used as example alias in default .ovprofile (see init-ovprofile)
welcome-to-openverse:
    #! /usr/bin/env bash
    # ASCII art courtesy of http://patorjk.com/software/taag/#p=display&f=Big&t=Openverse
    cat <<OPENVERSE
      ___   ____   ___  ____   __ __    ___  ____    _____   ___
     /   \ |    \ /  _]|    \ |  |  |  /  _]|    \  / ___/  /  _]
    |     ||  o  )  [_ |  _  ||  |  | /  [_ |  D  )(   \_  /  [_
    |  O  ||   _/    _]|  |  ||  |  ||    _]|    /  \__  ||    _]
    |     ||  | |   [_ |  |  ||  :  ||   [_ |    \  /  \ ||   [_
    |     ||  | |     ||  |  | \   / |     ||  .  \ \    ||     |
     \___/ |__| |_____||__|__|  \_/  |_____||__|\_|  \___||_____|
    OPENVERSE

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
    ([ ! -f indexer_worker/.env ] && cp indexer_worker/env.template indexer_worker/.env)   || true
    ([ ! -f api/.env ] && cp api/env.template api/.env) || true

##########
# Docker #
##########

DOCKER_FILE := "-f docker-compose.yml"
EXEC_DEFAULTS := if IS_CI == "" { "" } else { "-T" }

export CATALOG_PY_VERSION := `just catalog/py-version`
export CATALOG_AIRFLOW_VERSION := `just catalog/airflow-version`
export INDEXER_WORKER_PY_VERSION := `just indexer_worker/py-version`
export API_PY_VERSION := `just api/py-version`
export API_PDM_HASH := `just api/pdm-hash`
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
    indexer_worker_py_version=$(just indexer_worker/py-version)
    frontend_node_version=$(just frontend/node-version)
    frontend_pnpm_version=$(just frontend/pnpm-version)
    pgcli_version=$(just api/pgcli-version)
    EOF

# Run `docker compose` configured with the correct files and environment
[positional-arguments]
dc *args:
    @{{ if IS_CI != "" { "just env" } else { "true" } }}
    env COMPOSE_PROFILES="{{ env_var_or_default("COMPOSE_PROFILES", "api,ingestion_server,frontend,catalog") }}" docker compose {{ DOCKER_FILE }} "$@"

# Build all (or specified) services
[positional-arguments]
build *args:
    just dc build "$@"

# List all services and their URLs and ports
@ps:
    # ps is a helper command & intermediate dependency, so it should not fail the whole
    # command if it fails
    python3 utilities/ps.py || true

# Also see `up` recipe in sub-justfiles
# Bring all Docker services up, in all profiles
[positional-arguments]
up *flags: env && ps
    #!/usr/bin/env bash
    set -eo pipefail
    while true; do
      if just dc up {{ if IS_CI != "" { "--quiet-pull" } else { "" } }} -d "$@" ; then
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
[positional-arguments]
down *flags:
    just dc down "$@"

# Take all services down then call the specified app's up recipe. ex.: `just dup catalog` is useful for restarting the catalog with new environment variables
dup app:
    just down && just {{ app }}/up

# Recreate all volumes and containers from scratch
recreate:
    just down -v
    just up --force-recreate --build
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
[positional-arguments]
exec +args:
    just dc exec -u {{ env_var_or_default("DC_USER", "root") }} {{ EXEC_DEFAULTS }} "$@"

# Execute statement in a new service container using Docker Compose
[positional-arguments]
run +args:
    just dc run --rm -u {{ env_var_or_default("DC_USER", "root") }} {{ EXEC_DEFAULTS }} "$@"

# Execute pgcli against one of the database instances
_pgcli container db_user_pass db_name db_host db_port="5432":
    just exec {{ container }} pgcli postgresql://{{ db_user_pass }}:{{ db_user_pass }}@{{ db_host }}:{{ db_port }}/{{ db_name }}

###########
# Cleanup #
###########

# Recursively list, and delete, all specified dirs from the repo
_prune pattern delete="false":
    find . -name '{{ pattern }}' -type d -prune {{ if delete == "true" { "-exec rm -rf '{}' +" } else { "" } }}

# Recursively list, and delete, all `node_modules/` from the repo
prune_node delete="false":
    @just _prune node_modules {{ delete }}

# Recursively list, and delete, all `.venv/` from the repo
prune_venv delete="false":
    @just _prune .venv {{ delete }}

# Recursively list, and delete, all `node_modules/` and `.venv/` from the repo
prune delete="false":
    @just prune_node {{ delete }}
    @just prune_venv {{ delete }}

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
[positional-arguments]
p package script *args:
    #!/usr/bin/env bash
    pnpm --filter {{ package }} run {{ script }} "${@:3}"

# Run eslint with --fix and default file selection enabled; used to enable easy file overriding whilst retaining the defaults when running --all-files
[positional-arguments]
eslint *args:
    #! /usr/bin/env bash
    just p '@openverse/eslint-plugin' build
    if [[ "$@" ]]; then
        files=("$@")
    else
        # default files
        files=(frontend automations/js packages/js .pnpmfile.cjs eslint.config.mjs prettier.config.js tsconfig.base.json)
    fi

    pnpm exec eslint \
        --max-warnings=0 \
        --no-warn-ignored \
        --fix \
        "${files[@]}"

# Alias for `just packages/js/k6/run` or `just p k6 run`
[positional-arguments]
@k6 *args:
    just packages/js/k6/run "$@"
