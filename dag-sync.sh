#!/bin/bash
# DAG sync script used in production to update the repo files when invoked.
# This can be run using cron at the desired DAG sync interval.
#
# Inputs:
#   - The first and only argument to the script should be the Slack hook URL target
#     for the output sync message.
#
# Inspired by https://stackoverflow.com/a/21005490/3277713 via torek CC BY-SA 3.0
set -e

SLACK_URL=$1
# https://stackoverflow.com/a/246128 via Dave Dopson CC BY-SA 4.0
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

# Update origin
git fetch origin
# Get new commit hash *one commit ahead* of this one
new=$(git rev-list --reverse --topo-order HEAD..origin/main | head -1)
# If there is no new commit hash to move to, nothing has changed, quit early
[ -z "$new" ] && exit
# Move ahead to this new commit
git reset --hard "$new"
# Pull out the subject from the new commit
subject=$(git log -1 --format='%s')


if [ -z "$SLACK_URL" ]
  then
  echo "Slack hook was not supplied! Updates will not be posted"
else
  curl "$SLACK_URL" \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"text":"Deployed: '"$subject"'","username":"DAG Sync","icon_emoji":":recycle:","blocks":[{"type":"section","text":{"type":"mrkdwn","text":"Deployed: <https://github.com/WordPress/openverse-catalog/commit/'"$new"'|'"$subject"'>"}}]}'
fi
