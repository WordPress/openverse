#!/bin/bash

set -e

function help_text() {
  cat << 'END'

  ,-.  ;-.  ,--. .  . .   , ,--. ,-.   ,-.  ,--.
 /   \ |  ) |    |\ | |  /  |    |  ) (   ` |
 |   | |-'  |-   | \| | /   |-   |-<   `-.  |-
 \   / |    |    |  | |/    |    |  \ .   ) |
  `-'  '    `--' '  ' '     `--' '  '  `-'  `--'

Docker entrypoint script for Openverse Airflow. Unless specified, all commands
will wait for the database to be ready and will upgrade the Airflow schema.

Usage:
  help - print this help text and exit
  init - create an admin user account before starting the scheduler+webserver
  server - start the scheduler+webserver
  (anything else) - run the command provided
END
}


function header() {
  size=${COLUMNS:-80}
  # Print centered text between two dividers of length $size
  printf '#%.0s' $(seq 1 $size) && echo
  printf "%*s\n" $(( (${#1} + size) / 2)) "$1"
  printf '#%.0s' $(seq 1 $size) && echo
}

if [ "$1" == help ] || [ "$1" == --help ]; then help_text && exit 0; fi
sleep 0.1;  # The $COLUMNS variable takes a moment to populate

# Wait for postgres
header "WAITING FOR POSTGRES"
python wait_for_db.py
# Upgrade the database -- command is idempotent.
header "MIGRATING DATABASE"
airflow db upgrade
if [[ "$1" == "init" ]]; then
  header "CREATING ADMIN USER"
  airflow users create -r Admin -u airflow -f Air -l Flow -p airflow --email airflow@example.org
fi

case "$1" in
  init|server|"")
    # Start scheduler and webserver in same container
    header "STARTING AIRFLOW"
    airflow scheduler &
    exec airflow webserver
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    header "RUNNING \"$*\""
    exec "$@"
    ;;
esac
