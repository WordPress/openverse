import os


DATABASE_CONNECTION = os.getenv(
    "DATABASE_CONN", "postgresql+psycopg2://deploy:deploy@localhost/openledger"
)

# Attribution events stream configuration
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
KAFKA_TOPIC_NAME = os.getenv("KAFKA_TOPIC", "attribution_events_dev")
ATTRIBUTION_LOGFILE = os.getenv("LOGFILE", "/var/log/attribution_worker.log")
