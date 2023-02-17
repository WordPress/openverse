set dotenv-load := false

# Meaning of Just prefixes:
# @ - Quiet recipes (https://github.com/casey/just#quiet-recipes)
# _ - Private recipes (https://github.com/casey/just#private-recipes)

# Show all available recipes, also recurses inside nested justfiles
@_default:
  just --list --unsorted
  cd automations/python && just
  cd automations/js && just

#######
# Dev #
#######

# Install all dependencies
@install:
    just automations/python/install
    just automations/js/install

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
