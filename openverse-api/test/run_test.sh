#!/bin/bash

red="\e[31m"
green="\e[32m"
endcol="\e[0m"

# Specify a file as the first argument to restrict the test to that file only.
# ```
# $	./test/run_test.sh test/audio_integration_test.py
# ```
TEST_ARG="${1:-test/}"

# Local environments don't have valid certificates; suppress this warning.
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
export INTEGRATION_TEST_URL="http://localhost:8000"

PYTHONPATH=. \
DJANGO_SETTINGS_MODULE='catalog.settings' \
DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-ny#b__$f6ry4wy8oxre97&-68u_0lk3gw(z=d40_dxey3zw0v1}" \
DJANGO_DATABASE_NAME="${DJANGO_DATABASE_NAME:-openledger}" \
DJANGO_DATABASE_USER="${DJANGO_DATABASE_USER:-deploy}" \
DJANGO_DATABASE_PASSWORD="${DJANGO_DATABASE_PASSWORD:-deploy}" \
DJANGO_DATABASE_HOST="${DJANGO_DATABASE_HOST:-localhost}" \
REDIS_HOST="${REDIS_HOST:-localhost}" \
pytest -s --disable-pytest-warnings $TEST_ARG

succeeded=$?
if [[ $succeeded -eq 0 ]]; then
	printf "${green}:-) All tests passed${endcol}\n"
else
  printf "Full system logs:\n"
  docker-compose logs
	printf "${red}:'( Some tests did not pass${endcol}\n"
fi
exit $succeeded
