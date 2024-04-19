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
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# Update origin
git fetch origin
# Get new commit hash *one commit ahead* of this one
new=$(git rev-list --reverse --topo-order HEAD..origin/main | head -1)
# If there is no new commit hash to move to, nothing has changed, quit early
if [ -z "$new" ]; then
  echo "No new commits, nothing has changed, nothing to do."
  exit
fi

# Move ahead to this new commit
git reset --hard "$new"
# Verify if have /dags/ in the last commit
have_dag=$(git log -p -1 "$new" --pretty=format: --name-only | grep "catalog/dags/")
# If there is no files under /dags/ folder, no need to notify, quit early
if [ -z "$have_dag" ]; then
  echo "No changes to DAGs, nothing to do."
  exit
fi

# Pull out the subject from the new commit
subject=$(git log -1 --format='%s')
# Swap the < & > characters for their HTML entities so they aren't
# interpreted as delimiters by Slack
subject=${subject//>/&gt;}
subject=${subject//</&lt;}

if [ -z "$SLACK_URL" ]; then
  echo "Slack hook was not supplied! Updates will not be posted"
else
  curl "$SLACK_URL" \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"text":"Deployed: '"$subject"'","username":"DAG Sync","icon_emoji":":recycle:","blocks":[{"type":"section","text":{"type":"mrkdwn","text":"Deployed: <https://github.com/WordPress/openverse/commit/'"$new"'|'"$subject"'>"}}]}'
fi
