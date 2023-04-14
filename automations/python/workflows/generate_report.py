"""Generate a completion report for the CI + CD workflow."""

import json
import os
import sys
from collections import defaultdict


server_url = os.environ.get("SERVER_URL")
repository = os.environ.get("REPOSITORY")
run_id = os.environ.get("RUN_ID")

jobs = ["emit-docs", "publish-images", "deploy-frontend", "deploy-api"]

results = {}
counts = defaultdict(int)

for job_name in jobs:
    result = os.environ.get(f"{job_name.replace('-', '_')}_result".upper())
    results[job_name] = result
    counts[result] += 1

payload = {
    "text": ", ".join(f"{count} {result}" for result, count in counts.items()),
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"<{server_url}/{repository}/actions/runs/{run_id}|"
                    "Click here to review the completed CI + CD workflow>."
                ),
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*{job_name}:*\n:workflow-{result}: {result}",
                }
                for job_name, result in results.items()
            ],
        },
    ],
}

with open(os.environ.get("GITHUB_OUTPUT"), "a", encoding="utf-8") as gh_out:
    for dest in [sys.stdout, gh_out]:
        print(f"payload={json.dumps(payload)}", file=dest)
