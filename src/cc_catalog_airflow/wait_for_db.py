import logging
import os
import sys
import time

import sqlalchemy as db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__file__)

TRIES = 10
CONN_ID = os.getenv('AIRFLOW__CORE__SQL_ALCHEMY_CONN')


def main():
    db_available = _wait_for_db()
    if not db_available:
        logger.error(f'Could not connect to DB using conn_id {CONN_ID}')
        sys.exit(1)
    else:
        sys.exit(0)


def _wait_for_db(tries=TRIES, conn_id=CONN_ID):
    engine = db.create_engine(conn_id)
    success = False
    for i in range(1, TRIES + 1):
        try:
            logger.info(f'Testing DB connection {conn_id}')
            connection = engine.connect()
            connection.close()
            success = True
            break
        except db.exc.OperationalError as oe:
            logger.info('DB not yet available')
            logger.debug(f'Error was:  {oe}')
            logger.info(f'Waiting {i} seconds...')
            # Back off with each loop to give the DB a chance to appear.
            time.sleep(i)
    return success


if __name__ == '__main__':
    main()
