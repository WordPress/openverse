#!/bin/bash

set -e

function help_text() {
  cat <<'END'

  ,-.  ;-.  ,--. .  . .   , ,--. ,-.   ,-.  ,--.
 /   \ |  ) |    |\ | |  /  |    |  ) (   ` |
 |   | |-'  |-   | \| | /   |-   |-<   `-.  |-
 \   / |    |    |  | |/    |    |  \ .   ) |
  `-'  '    `--' '  ' '     `--' '  '  `-'  `--'

Docker entrypoint script for Openverse Airflow. This uses the upstream Airflow
entrypoint under the hood. For help running commands, see
https://airflow.apache.org/docs/docker-stack/entrypoint.html#executing-commands
Unless specified, all commands will wait for the database to be ready and
will upgrade the Airflow schema.

Usage:
  help - print this help text and exit
  bash [...] - drop into a bash shell or run a bash command/script
  python [ ... ] - drop into a python shell or run a python command/script
  (anything else) - interpreted as an argument to "airflow [ argument ]"
END
}

function header() {
  size=${COLUMNS:-80}
  # Print centered text between two dividers of length $size
  printf '#%.0s' $(seq 1 "$size") && echo
  printf "%*s\n" $(((${#1} + size) / 2)) "$1"
  printf '#%.0s' $(seq 1 "$size") && echo
}

if [ "$1" == help ] || [ "$1" == --help ]; then help_text && exit 0; fi
sleep 0.1 # The $COLUMNS variable takes a moment to populate

# Reformat Slack Airflow connections
header "MODIFYING ENVIRONMENT"
# Loop through environment variables, relying on naming conventions.
# Bash loops with pipes occur in a subprocess, so we need to do some special
# subprocess manipulation via <(...) syntax to allow the `export` calls
# to propagate to the outer shell.
# See: https://unix.stackexchange.com/a/402752
while read -r var_string; do
  # get the variable name
  var_name=$(expr "$var_string" : '^\([A-Z_]*\)')
  echo "Variable Name: $var_name"
  # get the old value
  old_value=$(expr "$var_string" : '^[A-Z_]*=\(http.*\)$')
  echo "    Old Value: $old_value"
  # call python to url encode the http clause
  url_encoded=$(python -c "from urllib.parse import quote_plus; import sys; print(quote_plus(sys.argv[1]))" "$old_value")
  # prepend http://
  new_value='http://'$url_encoded
  echo "    New Value: $new_value"
  # set the environment variable
  export "$var_name"="$new_value"

  # only include Slack airflow connections
done < <(env | grep "^AIRFLOW_CONN_SLACK*")

exec /entrypoint "$@"
