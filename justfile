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
    just precommit

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
    pnpm install

# Run `render-jinja.js` with given input file, output file and context
render in_file out_file ctx="{}":
    cd automations/js && node src/render-jinja.js {{ in_file }} {{ out_file }} {{ ctx }}

# Render `.pre-commit-config.yaml`
render-precommit:
    just render .pre-commit-config.local.yaml.jinja .pre-commit-config.yaml

# Render `prettier.config.js`
render-prettier:
    just render prettier.config.js.jinja prettier.config.js
