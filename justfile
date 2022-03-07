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

@_monitor-env environment:
    if [ ! -f monitoring/.env.{{ environment }} ]  && [ "{{ environment }}" != "local" ]; then \
        echo "Missing .env.{{ environment }} file"; \
        echo "Run 'just mkenv {{ environment }}' to generate a new one"; \
        exit 1; \
    fi

    just mkenv {{ environment }}


@mkenv environment:
    if [ -f monitoring/.env.{{ environment }} ]; then \
        echo "Using existing .env.{{ environment }}"; \
        exit 0; \
    fi

    printf "$(cat monitoring/.env.template)\nUSER_ID=$(id -u):$(id -g)" >> monitoring/.env.{{ environment }}


mkpromconf +args="local":
    python monitoring/create_prometheus_yaml.py {{ args }}

_monitor-dc environment="local" *args="": (_monitor-env environment)
    docker-compose --env-file=monitoring/.env.{{ environment }} -f monitoring/docker-compose.yml {{ args }}

# Start local monitoring stack
@monitor environment="local" args="":
    just mkpromconf {{ environment }} --check
    just _monitor-dc {{ environment }} up -d {{ args }}
    echo 'Prometheus running at localhost:58233'
    echo 'Grafana running at localhost:58234'

@monitor-logs service="":
    just _monitor-dc "logs {{ service }}"

@remonitor:
    just _monitor-dc "down -v"
    just monitor "--force-recreate --build"

@grafana-cli args="":
    just _monitor-dc "exec grafana grafana-cli {{ args }}"
