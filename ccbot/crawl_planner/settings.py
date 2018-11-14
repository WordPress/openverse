import os

# Crawl planner settings
DATABASE_HOST = os.getenv('CCCATALOG_DATABASE_HOST', 'localhost')
DATABASE_PORT = int(os.getenv('CCCATALOG_DATABASE_PORT', 5432))
DATABASE_PASSWORD = os.getenv('CCCATALOG_DATABASE_PASSWORD', 'deploy')
CCCATALOG_API_URL = os.getenv('CCCATALOG_API_URL', 'http://localhost:8000')

# Request-per-second limits for each rate limit strategy. If you change these
# numbers, you must regenerate the crawl plan.
VERY_LIGHT_RPS = 1
LIGHT_RPS = 3
MODERATE_RPS = 4
HEAVY_RPS = 5
# ~1.72MM requests per day
VERY_HEAVY_RPS = 20
# ~17.2MM requests per day. Reserved for the largest content providers.
# MAX_RPS = 200

# Crawl executor settings
CLUSTER_REST_URL = os.getenv('CLUSTER_REST_HOST', 'http://localhost:5343')
# Kafka brokers
CLUSTER_BROKER_HOSTS = os.getenv('CLUSTER_KAFKA_HOST', 'localhost:9092')
CLUSTER_INCOMING_TOPIC = os.getenv('CLUSTER_INCOMING_TOPIC', 'ccbot.incoming')
