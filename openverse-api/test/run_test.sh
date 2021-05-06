#!/bin/bash
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
pytest -s --disable-pytest-warnings test/v1_integration_test.py

succeeded=$?
if [ $succeeded != 0 ]; then
  echo 'Tests failed. Full system logs: '
  docker-compose logs
fi
exit $succeeded
