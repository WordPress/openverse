import os

DATABASE_CONNECTION = os.getenv(
        'DATABASE_CONN', 'postgres+psycopg2://deploy:deploy@localhost/openledger'
)
