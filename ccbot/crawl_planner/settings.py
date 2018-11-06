import os

DATABASE_HOST = os.getenv('CCCATALOG_DATABASE_HOST', 'localhost')
DATABASE_PORT = 5432
DATABASE_PASSWORD = os.getenv('CCCATALOG_DATABASE_PASSWORD', 'deploy')
CCCATALOG_API_URL = os.getenv('CCCATALOG_API_URL', 'localhost:8000')

# Maximum per-domain rate limit; this is appropriate for providers with 
# large amounts of content. Smaller content providers have more conservative
# rate limits applied. Fine-grained per-spider rate limits are set in the
# crawler configuration and are not overridden by this setting.
REQUESTS_PER_SECOND_CEILING = \
    int(os.getenv('REQUESTS_PER_SECOND_CEILING', 1000))
