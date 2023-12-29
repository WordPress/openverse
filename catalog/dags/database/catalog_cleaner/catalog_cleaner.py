"""
Catalog Data Cleaner DAG

Use CSV files created during the clean step of the ingestion process to bring the
changes into the catalog.
"""

import logging
from datetime import timedelta
from pathlib import Path

from airflow.decorators import dag
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.sql import PGExecuteQueryOperator, PostgresHook, RETURN_ROW_COUNT


logger = logging.getLogger(__name__)

DAG_ID = "catalog_cleaner"
pg = PostgresHook()


def load_temp_tables(columns: list[str]):
    copy_sql = (
        "COPY cleaned_image_{column} (identifier, {column}) FROM STDIN "
        "DELIMITER E'\t' CSV QUOTE '''' "
    )
    for column in columns:
        file_path = str(Path(__file__).parent / f"{column}.tsv")
        pg.copy_expert(copy_sql.format(column=column), file_path)


def count_dirty_rows(columns: list[str]):
    count_sql = (
        "SELECT COUNT(identifier) FROM cleaned_image_{} AS tmp "
        "WHERE tmp.identifier IN (SELECT identifier FROM image)"
    )
    for column in columns:
        count = pg.get_first(count_sql.format(column))[0]
        logger.info(f"Dirty rows found for ´{column}´: {count}")


def update_batches(column: str, total_row_count: int, batch_size: int):
    pg_ = PostgresHook(log_sql=False)
    batch_start = updated_count = 0
    update_sql = """
        UPDATE image SET {column} = tmp.{column}, updated_on = NOW()
        FROM cleaned_image_{column} AS tmp
        WHERE image.identifier = tmp.identifier AND image.identifier IN (
            SELECT identifier FROM cleaned_image_{column}
            WHERE row_id > {batch_start} AND row_id <= {batch_end}
            FOR UPDATE SKIP LOCKED
        );
    """

    while batch_start <= total_row_count:
        batch_end = batch_start + batch_size
        logger.info(f"Going through rows with id {batch_start:,} to {batch_end:,}.")
        query = update_sql.format(
            column=column, batch_start=batch_start, batch_end=batch_end
        )
        count = pg_.run(query, handler=RETURN_ROW_COUNT)

        batch_start += batch_size
        updated_count += count
        logger.info(f"Updated {updated_count:,} rows of the ´{column}´ column so far.")


def update_from_temp_tables(columns: list[str], batch_size):
    for column in columns:
        total_row_count = pg.get_first(
            f"SELECT COUNT(identifier) FROM cleaned_image_{column}"
        )[0]
        logger.info(f"Total rows found for ´{column}´: {total_row_count}")
        update_batches(column, total_row_count, int(batch_size))


@dag(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(days=7),
    },
    schedule=None,
    catchup=False,
    tags=["database"],
    doc_md=__doc__,
    params={
        "batch_size": Param(
            default=10000,
            type="integer",
            description=("The number of records to update per batch."),
        ),
    },
)
def catalog_cleaner():
    columns = {
        "url": 3000,
        "creator_url": 2000,
        # "foreign_landing_url": 1000
    }
    create_sql = """
    DROP TABLE IF EXISTS cleaned_image_{column};
    CREATE UNLOGGED TABLE cleaned_image_{column} (
        identifier uuid PRIMARY KEY,
        {column} character varying({length}) NOT NULL,
        row_id SERIAL
    );
    """

    create = PGExecuteQueryOperator(
        task_id="create_temporary_tables",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="\n".join(
            [
                create_sql.format(column=col, length=length)
                for col, length in columns.items()
            ]
        ),
        execution_timeout=timedelta(minutes=1),
    )

    load = PythonOperator(
        task_id="load_temporary_tables",
        python_callable=load_temp_tables,
        op_kwargs={"columns": columns.keys()},
        execution_timeout=timedelta(hours=1),
    )

    count = PythonOperator(
        task_id="count_dirty_rows",
        python_callable=count_dirty_rows,
        op_kwargs={"columns": columns.keys()},
        execution_timeout=timedelta(minutes=15),
    )

    update = PythonOperator(
        task_id="update_from_temporary_tables",
        python_callable=update_from_temp_tables,
        op_kwargs={"columns": columns.keys(), "batch_size": "{{ params.batch_size }}"},
        execution_timeout=timedelta(hours=1),
    )

    # drop = PGExecuteQueryOperator(
    #     task_id="drop_temp_tables",
    #     postgres_conn_id=POSTGRES_CONN_ID,
    #     sql="\n".join(f"DROP TABLE cleaned_image_{column};" for column in columns.keys()),
    #     execution_timeout=timedelta(minutes=1)
    # )

    create >> load >> count >> update
    # update >> drop


catalog_cleaner()
