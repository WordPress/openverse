import os

DATABASE_HOST = os.getenv('CCCATALOG_DATABASE_HOST', 'localhost')
DATABASE_PORT = int(os.getenv('CCCATALOG_DATABASE_PORT', 5432))
DATABASE_PASSWORD = os.getenv('CCCATALOG_DATABASE_PASSWORD', 'deploy')
CCCATALOG_API_URL = os.getenv('CCCATALOG_API_URL', 'http://localhost:8000')

# Request-per-second limits for each rate limit strategy.
VERY_LIGHT_RPS = 1
LIGHT_RPS = 3
MODERATE_RPS = 4
HEAVY_RPS = 5
# ~1.72MM requests per day
VERY_HEAVY_RPS = 20
# ~17.2MM requests per day. Reserved for the largest content providers.
# MAX_RPS = 200
