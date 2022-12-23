#! /usr/bin/env sh

set -e

if [ -z "$SKIP_PRE_COMMIT" ] && [ ! -f ./pre-commit.pyz ]
then
  echo "downloading pre-commit"
  curl \
    ${GITHUB_TOKEN:+ --header "Authorization: Bearer ${GITHUB_TOKEN}"} \
    https://api.github.com/repos/pre-commit/pre-commit/releases/latest \
  | grep -o 'https://.*\.pyz' -m 1 \
  | xargs \
  | xargs curl -fsJo pre-commit.pyz -L

  echo "installing pre-commit"
  pnpm pc:install
else
  echo "skipping pre-commit installation"
fi
