"""
One-time run DAG to remove progressively all the old Flickr thumbnails,
as they were determined to be unsuitable for the Openverse UI requirements.
"""

import logging
from datetime import timedelta
from textwrap import dedent

from airflow.decorators import dag, task

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.slack import send_message
from common.sql import PostgresHook


logger = logging.getLogger(__name__)


DAG_ID = "flickr_thumbnails_removal"


@dag(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(days=7),
    },
    schedule=None,
    catchup=False,
    doc_md=__doc__,
)
def flickr_thumbnails_removal():
    pg = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    select_conditions = "FROM image WHERE provider = 'flickr' AND thumbnail IS NOT NULL"

    @task()
    def count():
        num_thumbs = pg.get_first(f"SELECT COUNT(*) {select_conditions}")[0]
        logger.info(f"Flickr thumbnails found: {num_thumbs}.")

        return num_thumbs

    @task()
    def delete(num_thumbs):
        log_sql = True
        if num_thumbs == 0:
            logger.info("No Flickr thumbnails found.")

        while num_thumbs > 0:
            query = dedent(
                f"""
                UPDATE image SET thumbnail = NULL WHERE identifier IN (
                    SELECT identifier {select_conditions}
                    FETCH FIRST 10000 ROWS ONLY FOR UPDATE SKIP LOCKED
                )
                """
            )
            pg.run(query, log_sql=log_sql)
            num_thumbs -= 10000
            logger.info(
                f"Flickr thumbnails left: {num_thumbs if num_thumbs > 0 else 0}."
            )
            log_sql = False

    @task()
    def report():
        msg = (
            "All Flickr thumbnails were successfully removed. "
            f"The `{DAG_ID}` DAG can be retired."
        )
        send_message(msg, DAG_ID)

    num_thumbs = count()
    d = delete(num_thumbs)
    r = report()
    d >> r


flickr_thumbnails_removal()
