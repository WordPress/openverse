from decouple import config


DATABASE_CONNECTION = config(
    "DATABASE_CONN",
    default="postgresql+psycopg2://deploy:deploy@localhost/openledger",
)

# Attribution events stream configuration
KAFKA_HOSTS = config("KAFKA_HOSTS", default="kafka:9092")
KAFKA_TOPIC_NAME = config("KAFKA_TOPIC", default="attribution_events_dev")
ATTRIBUTION_LOGFILE = config("LOGFILE", default="/var/log/attribution_worker.log")
