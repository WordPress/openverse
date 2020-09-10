import os

DATABASE_CONNECTION = os.getenv(
    'DATABASE_CONN', 'postgres+psycopg2://deploy:deploy@localhost/analytics'
)

KAFKA_HOSTS = os.getenv('KAFKA_HOSTS', 'kafka:9092')
