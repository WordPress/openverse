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

# Run pre-commit to lint and reformat all files
lint:
    python3 pre-commit.pyz run --all-files

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
    just render templates/.pre-commit-config.local.yaml.jinja .pre-commit-config.yaml

# Render `prettier.config.js`
render-prettier:
    just render templates/prettier.config.js.jinja prettier.config.js

# Render GitHub issue & PR templates
render-github:
    just render templates/pull_request_template.md.jinja .github/PULL_REQUEST_TEMPLATE/pull_request_template.md

# Render all templates (shortcut for easy iteration)
render-templates:
    just render-precommit
    just render-prettier
    just render-github
