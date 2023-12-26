import logging as log
import time

import psycopg2
from decouple import config

DATABASE_HOST = config("DATABASE_HOST", default="localhost")
DATABASE_PORT = config("DATABASE_PORT", default=5432, cast=int)
DATABASE_USER = config("DATABASE_USER", default="deploy")
DATABASE_PASSWORD = config("DATABASE_PASSWORD", default="deploy")
DATABASE_NAME = config("DATABASE_NAME", default="openledger")


def database_connect(
    autocommit: bool = False,
    timeout: int = 5,
    attempt_reconnect: bool = True,
):
    """
    Repeatedly try to connect to the downstream (API) database until successful
    (unless otherwise specified).

    :return: A database connection object
    """
    while True:
        try:
            conn = psycopg2.connect(
                dbname=DATABASE_NAME,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                connect_timeout=timeout,
            )
            if autocommit:
                conn.set_session(autocommit=True)
        except psycopg2.OperationalError as e:
            if not attempt_reconnect:
                raise e
            log.exception(e)
            log.error("Reconnecting to database in 5 seconds. . .")
            time.sleep(5)
            continue
        break

    return conn
