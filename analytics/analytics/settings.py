from decouple import Csv, config


VERSION = config("VERSION", default="1.0.0")

ORIGINS = config(
    "ORIGINS",
    cast=Csv(),
    default=",".join(
        [
            "https://search.openverse.engineering",
            "https://search-dev.openverse.engineering",
            "https://wordpress.org",
        ]
    ),
)

DATABASE_CONNECTION = config(
    "DATABASE_CONN",
    default="postgresql+psycopg2://deploy:deploy@localhost/openledger",
)

# Attribution events stream configuration
KAFKA_HOSTS = config("KAFKA_HOSTS", default="kafka:9092")
KAFKA_TOPIC_NAME = config("KAFKA_TOPIC", default="attribution_events_dev")
ATTRIBUTION_LOGFILE = config("LOGFILE", default="/var/log/attribution_worker.log")
IGNORED_REFERRER = config("IGNORED_REFERRER", default="wordpress.org")
