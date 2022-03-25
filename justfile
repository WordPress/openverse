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
    cd python && pipenv run pre-commit install

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
