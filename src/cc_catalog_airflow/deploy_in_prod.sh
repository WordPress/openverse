#!/bin/bash
#
# This script shows git status, asks for confirmation, then runs the steps
# necessary to deploy the Apache Airflow webserver container (and dependencies)
# to production.

set -o errexit
set -o errtrace
set -o nounset

trap '_es=${?};
    printf "${0}: line ${LINENO}: \"${BASH_COMMAND}\"";
    printf " exited with a status of ${_es}\n";
    exit ${_es}' ERR

deploy_with_docker_compose() {
    docker-compose -f docker-compose.yml build webserver
    docker-compose -f docker-compose.yml up -d webserver
}

git status

echo "Are you sure you want to deploy a production Airflow container?"
read -r -p "Type 'YES' in all caps to confirm >  " response
if [[ "$response" == "YES" && -f .env ]]; then
    echo "Typed YES, and .env exists.  Deploying..."
    deploy_with_docker_compose
else
    echo "Canceling"
fi

