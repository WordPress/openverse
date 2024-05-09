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

# Set up Airflow Variable defaults with descriptions automatically
# List all existing airflow variables
output=$(airflow variables list -o plain)
found_existing_vars=true

# if there are no existing variable, print this notification and continue
if [[ -z $output || $output == "No data found" ]]; then
  header "No existing variables found, proceeding to set all variables"
  found_existing_vars=false
fi

# Initialize an empty array to store the variables from the output
existing_variables=()

# Iterate through each variable and add it to $existing_variables
while IFS= read -r variable; do
  # skip airflow's default descriptive 'key' output
  if [[ $variable == "key" ]]; then
    continue
  fi
  # Append the current variable to the array
  existing_variables+=("$variable")
done <<<"$output"

if $found_existing_vars; then
  header "Found the following existing variables(The values of these will not be overwritten):"
  for variable in "${existing_variables[@]}"; do
    echo "$variable"
  done
fi

# now iterate through each row of variables.tsv and and only
# run airflow variables set --description <description> <key> <value>
# if the key doesn't already exist in the database i.e not found in
# $existing_variables
while IFS=$'\t' read -r column1 column2 column3; do
  # skip the first meta row or a row with empty data
  if [[ $column3 == "description" ]] || [[ -z $column2 ]]; then
    continue
  fi

  # check if current key already exists
  matched=false
  for variable in "${existing_variables[@]}"; do
    if [[ $variable == "$column1" ]]; then
      matched=true
    fi
  done

  if [ "$column1" != "Key" ] && ! $matched; then
    airflow variables set --description "$column3" "$column1" "$column2"
  fi
done <"variables.tsv"

# Print the new variables list
new_varibles_list=$(airflow variables list -o plain)
header "The following variables are now set:"
echo "$new_varibles_list"

# if the last line in variables.tsv did not correctly terminate
# with a new line character then this variable would not be empty
# and this means the last line would not be read correctly.
if [ -n "$column1" ]; then
  header "Missing new line character detected!!!"
  echo -e "Last variable added to variables.tsv might not be picked up,\nensure it ends with a new line character and retry."
fi

exec /entrypoint "$@"
