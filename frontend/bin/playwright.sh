#! /usr/bin/env sh
set -e

package_manager() {
  grep packageManager ../package.json | awk '{print $2}' | sed 's/[",]//g'
}

version() {
  pnpm ls --depth=0 | grep -e playwright | awk '{print $2}'
}

PACKAGE_MANAGER=$(package_manager)
export PACKAGE_MANAGER
export USER_ID="${USER_ID:-$(id -u)}"
export PLAYWRIGHT_ARGS="$*"
PLAYWRIGHT_VERSION=$(version)
export PLAYWRIGHT_VERSION
export TEST_COMMAND="${TEST_COMMAND:-test:playwright:local}"

pnpm i18n:get-translations --en-only

echo Running Playwright v"$PLAYWRIGHT_VERSION" as "$USER_ID" with Playwright arguments "$PLAYWRIGHT_ARGS" under package manager "$PACKAGE_MANAGER"

docker-compose -f docker-compose.playwright.yml up --build --force-recreate --exit-code-from playwright --remove-orphans

docker-compose -f docker-compose.playwright.yml down
