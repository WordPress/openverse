"""
Catalog Data Cleaner DAG

Use TSV files created during the clean step of the ingestion process to bring the
changes into the catalog.
"""

import logging
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.sql import PGExecuteQueryOperator, single_value
from database.batched_update.batched_update import run_sql
from database.catalog_cleaner import constants


logger = logging.getLogger(__name__)

DAG_ID = "catalog_cleaner"


@task
def count_dirty_rows(temp_table_name: str, task: AbstractOperator = None):
    count = run_sql.function(
        dry_run=False,
        sql_template=f"SELECT COUNT(*) FROM {temp_table_name}",
        query_id=f"{temp_table_name}_count",
        handler=single_value,
        task=task,
    )
    logger.info(f"Found {count:,} rows in the `{temp_table_name}` table.")
    return count


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
        "s3_bucket": Param(
            default="openverse-catalog",
            type="string",
            description="The S3 bucket where the TSV file is stored.",
        ),
        "s3_path": Param(
            default="shared/data-refresh-cleaned-data/<file_name>.tsv",
            type="string",
            description="The S3 path to the TSV file within the bucket.",
        ),
        "column": Param(
            type="string", description="The column of the table to apply the updates."
        ),
        # "table": Param(type="str", description="The media table to update."),
        "batch_size": Param(
            default=10000,
            type="integer",
            description="The number of records to update per batch.",
        ),
    },
)
def catalog_cleaner():
    aws_region = Variable.get("AWS_DEFAULT_REGION", default_var="us-east-1")
    column = "{{ params.column }}"
    temp_table_name = f"temp_cleaned_image_{column}"

    create = PGExecuteQueryOperator(
        task_id="create_temp_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.CREATE_SQL.format(temp_table_name=temp_table_name, column=column),
        execution_timeout=timedelta(minutes=1),
    )

    load = PGExecuteQueryOperator(
        task_id="load_temp_table_from_s3",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql=constants.IMPORT_SQL.format(
            temp_table_name=temp_table_name,
            column=column,
            bucket="{{ params.s3_bucket }}",
            s3_path_to_file="{{ params.s3_path }}",
            aws_region=aws_region,
        ),
        execution_timeout=timedelta(hours=1),
    )

    count = count_dirty_rows.override(
        trigger_rule=TriggerRule.NONE_FAILED,
    )(temp_table_name)

    # update = PythonOperator(
    #     task_id="update_from_temporary_tables",
    #     python_callable=update_from_temp_tables,
    #     op_kwargs={"columns": columns.keys(), "batch_size": "{{ params.batch_size }}"},
    #     execution_timeout=timedelta(hours=1),
    # )

    # drop = PGExecuteQueryOperator(
    #     task_id="drop_temp_tables",
    #     postgres_conn_id=POSTGRES_CONN_ID,
    #     sql="\n".join(f"DROP TABLE cleaned_image_{column};" for column in columns.keys()),
    #     execution_timeout=timedelta(minutes=1)
    # )

    create >> load >> count  # >> update
    # update >> drop


catalog_cleaner()
