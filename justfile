set dotenv-load := false

# Show all available recipes
default:
  @just --list --unsorted

#######
# Dev #
#######

# Install Python dependencies in Pipenv environments and JS dependencies
@install:
    just _py-install
    just _js-install

# Setup pre-commit as a Git hook
precommit:
    cd automations/python && pipenv run pre-commit install

# Run pre-commit to lint and reformat all files
lint:
    cd automations/python && pipenv run pre-commit run --all-files

##########
# Python #
##########

# Install dependencies for Python
_py-install:
    cd automations/python && pipenv install --dev

##############
# JavaScript #
##############

# Install dependencies for JavaScript
_js-install:
    cd automations/js && npm install

# Create a basic .env file for the monitoring environment; does not overwrite existing files
@mkenv environment:
    if [ -f monitoring/.env.{{ environment }} ]; then \
        echo "Using existing .env.{{ environment }}"; \
        exit 0; \
    fi

    printf "$(cat monitoring/.env.template)\nUSER_ID=$(id -u):$(id -g)" >> monitoring/.env.{{ environment }}

# Checks for the environment's .env file; automatically creates a new one for local but fails otherwise if the file is missing
@_monitor-env environment:
    if [ ! -f monitoring/.env.{{ environment }} ]  && [ "{{ environment }}" != "local" ]; then \
        echo "Missing .env.{{ environment }} file"; \
        echo "Run 'just mkenv {{ environment }}' to generate a new one"; \
        exit 1; \
    fi

    just mkenv {{ environment }}

# Creates a new prometheus configuration for the environment
mkpromconf +args="local":
    python monitoring/create_prometheus_yaml.py {{ args }}

# Execute a docker-compose command for the monitoring stack
_monitor-dc environment="local" *args="": (_monitor-env environment)
    docker-compose --env-file=monitoring/.env.{{ environment }} -f monitoring/docker-compose.yml {{ args }}

# Start local monitoring stack
@monitor environment="local" args="":
    just mkpromconf {{ environment }} --check
    just _monitor-dc {{ environment }} up -d {{ args }}
    echo 'Prometheus running at localhost:58233'
    echo 'Grafana running at localhost:58234'

# Retrieve logs for the local monitoring stack, optionally for a specific service
@monitor-logs service="":
    just _monitor-dc "logs {{ service }}"

# Recreate the local monitoring stack
@remonitor:
    just _monitor-dc "down -v"
    just monitor "--force-recreate --build"

# Execute a command in the grafana cli
@grafana-cli +args="":
    just _monitor-dc "exec grafana grafana-cli {{ args }}"
