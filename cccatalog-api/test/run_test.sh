#!/bin/bash
# Local environments don't have valid certificates; suppress this warning.
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
export INTEGRATION_TEST_URL="http://localhost:8000"
pytest -s
