"""
Python script Set slack user for workflow
"""

import json
import os
mapping = json.loads('${{ env.GH_SLACK_USERNAME_MAP }}')
GITHUB_USER = "${{ inputs.actor || github.actor }}"
slack_id = mapping[GITHUB_USER]
with open(os.getenv('GITHUB_ENV'), "a", encoding='utf-8') as env_file:
    env_file.write(f"SLACK_USER_ID={slack_id}")
    