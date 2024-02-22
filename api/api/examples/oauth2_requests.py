from api.examples.environment import ORIGIN, TOKEN


auth = f'-H "Authorization: Bearer {TOKEN}"' if TOKEN else ""

auth_register_curl = f"""
# Register for a key
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "My amazing project", "description": "To access Openverse API", "email": "user@example.com"}}' \\
  "{ORIGIN}/v1/auth_tokens/register/"
"""  # noqa: E501

auth_token_curl = f"""
# Get an access token token
curl \\
  -X POST \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d 'grant_type=client_credentials&client_id=<Openverse API client ID>&client_secret=<Openverse API client secret>' \\
  "{ORIGIN}/v1/auth_tokens/token/"
"""  # noqa: E501

auth_key_info_curl = f"""
curl \\
  {auth} \\
  "{ORIGIN}/v1/rate_limit/"
"""
