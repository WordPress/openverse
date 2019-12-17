#!/bin/bash
# Local environments don't have valid certificates; suppress this warning.
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
export INTEGRATION_TEST_URL="http://localhost:8000"
PYTHONPATH=. pytest -s --disable-pytest-warnings test/v1_integration_test.py
