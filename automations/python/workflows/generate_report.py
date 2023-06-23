"""Generate a completion report for the CI + CD workflow."""

import json
import os
from collections import defaultdict

from shared.actions import write_to_github_output


server_url = os.environ.get("SERVER_URL")
repository = os.environ.get("REPOSITORY")
run_id = os.environ.get("RUN_ID")
gh_slack_username_map = json.loads(os.environ.get("GH_SLACK_USERNAME_MAP", "{}"))
github_username = os.environ.get(
    "GITHUB_ACTOR"
)  # GitHub username of the actor that initiated the current workflow
commit_message = os.environ.get("COMMIT_MESSAGE")
commit_url = f"{server_url}/{repository}/commit/{os.environ.get('GITHUB_SHA')}"

slack_id = gh_slack_username_map.get(github_username)

jobs = ["emit-docs", "publish-images", "deploy-frontend", "deploy-api"]

results = {}
counts = defaultdict(int)

for job_name in jobs:
    result = os.environ.get(f"{job_name.replace('-', '_')}_result".upper())
    results[job_name] = result
    counts[result] += 1

user_mention = f"<@{slack_id}>" if slack_id else github_username

payload = {
    "text": ", ".join(f"{count} {result}" for result, count in counts.items()),
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"Hi {user_mention}, some CI + CD checks failed for your merge of <{commit_url}|{commit_message}>.\n"  # noqa: E501
                    "This _could_ indicate problems with deployments or tests introduced by your PR.\n"  # noqa: E501
                    "Please reply to this message with :ack: when seen, :github-approved: when resolved, or :issue_created: if it is unresolved and needs work. Link to any relevant issues you create.\n"  # noqa: E501
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
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Review CI + CD Workflow",
                    },
                    "url": f"{server_url}/{repository}/actions/runs/{run_id}",
                    "style": "primary",
                }
            ],
        },
    ],
}

lines = [f"payload={json.dumps(payload)}"]
write_to_github_output(lines)
