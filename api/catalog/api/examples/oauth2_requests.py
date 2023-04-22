import os


token = os.getenv("AUDIO_REQ_TOKEN", "DLBYIcfnKfolaXKcmMC8RIDCavc2hW")
origin = os.getenv("AUTH_REQ_ORIGIN", "https://api.openverse.engineering")

auth = f'-H "Authorization: Bearer {token}"' if token else ""

auth_register_curl = f"""
# Register for a key
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "My amazing project", "description": "To access Openverse API", "email": "user@example.com"}}' \\
  "{origin}/v1/auth_tokens/register/"
"""  # noqa: E501

auth_key_info_curl = f"""
curl \\
  {auth} \\
  "{origin}/v1/rate_limit/"
"""
