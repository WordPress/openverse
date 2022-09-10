#! /usr/bin/env bash

set -e

shellcheck source = ./.env.sh

source ./.env.sh || (echo "Please create a `.env.sh` file based on the `.env.sh.template` file." > /dev/stderr && false)

host=$1

auth_header="Authorization: Bearer $ACCESS_TOKEN"

concurrency=4

requests=100

q=$(./get_word.sh)

set -x

ab \
    -w \
    -v 3 \
    -c $concurrency \
    -n $requests \
    -T "application/json" \
    -H "$auth_header" \
    "$host/v1/images/?$q&page_size=500" > output.html

set +x

# fix root permissions
chown 1000:1000 output.html
