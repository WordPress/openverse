import logging as log
import time
from typing import NamedTuple

import psycopg2
from decouple import config


class DbConfig(NamedTuple):
    host: str
    port: int
    user: str
    password: str
    dbname: str


DB_API_CONFIG = DbConfig(
    host=config("DATABASE_HOST", default="localhost"),
    port=config("DATABASE_PORT", default=5432, cast=int),
    user=config("DATABASE_USER", default="deploy"),
    password=config("DATABASE_PASSWORD", default="deploy"),
    dbname=config("DATABASE_NAME", default="openledger"),
)

DB_UPSTREAM_CONFIG = DbConfig(
    host=config("UPSTREAM_DB_HOST", default="localhost"),
    port=config("UPSTREAM_DB_PORT", default=5433, cast=int),
    user=config("UPSTREAM_DB_USER", default="deploy"),
    password=config("UPSTREAM_DB_PASSWORD", default="deploy"),
    dbname=config("UPSTREAM_DB_NAME", default="openledger"),
)


def database_connect(
    autocommit: bool = False,
    dbconfig: DbConfig = DB_API_CONFIG,
    timeout: int = 5,
    attempt_reconnect: bool = True,
):
    """
    Repeatedly try to connect to the downstream (API) database until successful
    (unless otherwise specified).
    """
    while True:
        try:
            conn = psycopg2.connect(**dbconfig._asdict(), connect_timeout=timeout)
            if autocommit:
                conn.set_session(autocommit=True)
        except psycopg2.OperationalError as e:
            if not attempt_reconnect:
                return None
            log.exception(e)
            log.error("Reconnecting to database in 5 seconds. . .")
            time.sleep(5)
            continue
        break

    return conn
