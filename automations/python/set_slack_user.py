import json
import os
mapping = json.loads('${{ env.GH_SLACK_USERNAME_MAP }}')
github_user = "${{ inputs.actor || github.actor }}"
slack_id = mapping[github_user]
with open(os.getenv('GITHUB_ENV'), "a") as env_file:
    env_file.write(f"SLACK_USER_ID={slack_id}")