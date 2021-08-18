import os

API_URL = os.getenv('INTEGRATION_TEST_URL', 'http://localhost:8000')

KNOWN_ENVS = {
    'http://localhost:8000': 'LOCAL',
    'https://api.openverse.engineering': 'PRODUCTION',
    'https://api-dev.openverse.engineering': 'TESTING'
}