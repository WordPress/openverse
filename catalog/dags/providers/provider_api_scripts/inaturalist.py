"""
Provider:   iNaturalist

Output:     Records loaded to the image catalog table.

Notes:      The iNaturalist API is not intended for data scraping.
            <https://api.inaturalist.org/v1/docs/>
            But there is a full dump intended for sharing on S3.
            <https://github.com/inaturalist/inaturalist-open-data/tree/documentation/Metadata>
            Because these are exceptionally large normalized tables, as opposed to more document
            oriented API responses, we found that bringing the data into postgres first
            was the most effective approach. More detail in slack here:
            <https://wordpress.slack.com/archives/C02012JB00N/p1653145643080479?thread_ts=1653082292.714469&cid=C02012JB00N>
            We use the table structure defined here,
            <https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql>
            except for adding ancestry tags to the taxa table.
"""

import logging
import os
import time
import zipfile
from datetime import timedelta
from pathlib import Path

import pendulum
import requests
from airflow import XComArg
from airflow.exceptions import AirflowNotFoundException, AirflowSkipException
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from common.constants import AWS_CONN_ID, IMAGE, POSTGRES_CONN_ID, XCOM_PULL_TEMPLATE
from common.loader import provider_details, reporting, sql
from common.sql import PGExecuteQueryOperator, PostgresHook
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parents[1] / "provider_csv_load_scripts/inaturalist"
SOURCE_FILE_NAMES = ["photos", "observations", "taxa", "observers"]
LOADER_ARGS = {
    "postgres_conn_id": POSTGRES_CONN_ID,
    "identifier": "{{ ts_nodash }}",
    "media_type": IMAGE,
}
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/"))
COL_URL = "https://download.checklistbank.org/col/latest_coldp.zip"


class INaturalistDataIngester(ProviderDataIngester):
    providers = {"image": provider_details.INATURALIST_DEFAULT_PROVIDER}

    def get_next_query_params(self, prev_query_params=None):
        raise NotImplementedError(
            "Instead we use get_batches to dynamically create subtasks."
        )

    def get_response_json(self, query_params, **kwargs):
        raise NotImplementedError("TSV files from AWS S3 processed in postgres.")

    def get_batch_data(self, response_json):
        raise NotImplementedError("TSV files from AWS S3 processed in postgres.")

    def get_record_data(self, data):
        raise NotImplementedError("TSV files from AWS S3 processed in postgres.")

    @staticmethod
    def get_media_type(record):
        # This provider only supports Images via S3, though they have some audio files
        # on site and in the API.
        return IMAGE

    def endpoint(self):
        raise NotImplementedError("Normalized TSV files from AWS S3 means no endpoint.")

    @staticmethod
    def get_batches(
        batch_length: int,  # must be a positive, non-zero integer
        task: AbstractOperator,
    ):
        pg = PostgresHook(
            postgres_conn_id=POSTGRES_CONN_ID,
            default_statement_timeout=PostgresHook.get_execution_timeout(task),
        )
        min_id, max_id = pg.get_records(
            "SELECT min(photo_id), max(photo_id) FROM inaturalist.photos"
        )[0]
        if min_id is None or max_id is None:
            # This would only happen if there were no data loaded to inaturalist.photos
            # yet, but just in case.
            return
        # Return the list of batch starts and ends, which will be passed to op_args,
        # which expects each arg to be a list. So, it's a list of lists, not a list
        # of tuples.
        return [
            [(x, x + batch_length - 1)] for x in range(min_id, max_id, batch_length)
        ]

    @staticmethod
    def load_transformed_data(
        batch: tuple[int, int],
        intermediate_table: str,
        identifier: str,
        task: AbstractOperator,
        sql_template_file_name="transformed_table.template.sql",
    ):
        """
        Process a single batch of inaturalist photo ids. batch_start is the minimum
        photo_id for the batch. get_batches generates a list for xcoms to use in
        generating tasks that use this function.
        """
        start_time = time.perf_counter()
        (batch_start, batch_end) = batch
        pg = PostgresHook(
            postgres_conn_id=POSTGRES_CONN_ID,
            default_statement_timeout=PostgresHook.get_execution_timeout(task),
        )
        sql_template = (SCRIPT_DIR / sql_template_file_name).read_text()
        batch_number = int(batch_start / (batch_end - batch_start + 1)) + 1
        logger.info(f"Starting at photo_id {batch_start}, on batch {batch_number}.")
        # Load records to the intermediate table
        (loaded_records, max_id_loaded) = pg.get_records(
            sql_template.format(
                intermediate_table=intermediate_table,
                batch_start=batch_start,
                batch_end=batch_end,
            )
        )[0]
        logger.info(
            f"Inserted {loaded_records} into {intermediate_table}. "
            f"Last photo_id loaded was {max_id_loaded}, from batch {batch_number}."
        )
        # Run standard cleaning
        (missing_columns, foreign_id_dup) = sql.clean_intermediate_table_data(
            postgres_conn_id=POSTGRES_CONN_ID, identifier=identifier, task=task
        )
        # Add transformed records to the target catalog image table.
        # TO DO: Would it be better to use loader.upsert_records here? Would need to
        # trace back the parameters that need to be passed in for different stats.
        upserted_records = sql.upsert_records_to_db_table(
            postgres_conn_id=POSTGRES_CONN_ID,
            identifier=identifier,
            task=task,
            media_type=IMAGE,
        )
        logger.info(f"Upserted {upserted_records} records, from batch {batch_number}.")
        # Truncate the temp table
        pg.run(f"truncate table {intermediate_table};")
        # Return results for consolidation
        end_time = time.perf_counter()
        duration = end_time - start_time
        return {
            "loaded": loaded_records,
            "max_id_loaded": max_id_loaded,
            "missing_columns": missing_columns,
            "foreign_id_dup": foreign_id_dup,
            "upserted": upserted_records,
            "duration": duration,
        }

    @staticmethod
    def consolidate_load_statistics(all_results, ti):
        """
        all_results should be a list of all of the return_values from dynamically
        generated subtasks under load_transformed_data. This just totals the individual
        stats from each step.
        """
        if all_results is None:
            return
        else:
            METRICS = ["loaded", "missing_columns", "foreign_id_dup", "upserted"]
            metric_output = {}
            for metric in METRICS:
                metric_output[metric] = sum([x[metric] for x in all_results])
            # url dups are just a remainder, per common.loader.upsert_data
            metric_output["url_dup"] = (
                metric_output["loaded"]
                - metric_output["missing_columns"]
                - metric_output["foreign_id_dup"]
                - metric_output["upserted"]
            )
            metric_output.pop("loaded")
            # splitting metrics to be consistent with common.reporting.report_completion
            ti.xcom_push(key="duration", value=[x["duration"] for x in all_results])
            return {IMAGE: reporting.RecordMetrics(**metric_output)}

    @staticmethod
    def compare_update_dates(
        last_success: pendulum.DateTime | None, s3_keys: list, aws_conn_id=AWS_CONN_ID
    ):
        # if it was never run, assume the data is new
        if last_success is None:
            logger.info("No last success date, assuming iNaturalist data is new.")
            return
        s3 = S3Hook(aws_conn_id=aws_conn_id)
        s3_client = s3.get_client_type()
        for key in s3_keys:
            # this will error out if the files don't exist, and bubble up as an
            # informative failure
            last_modified = s3_client.head_object(
                Bucket="inaturalist-open-data", Key=key
            )["LastModified"]
            logger.info(
                f"{key} was last modified on s3 on "
                f"{last_modified.strftime('%Y-%m-%d %H:%M:%S')}."
            )
            # if any file has been updated, let's pull them all
            if last_success < last_modified:
                logger.info(
                    f"{key} was updated on s3 since the last dag run on "
                    f"{last_success.to_datetime_string()}."
                )
                return
        # If no files have been updated, skip the DAG
        raise AirflowSkipException(
            "Nothing new to ingest since last successful dag run on "
            f"{last_success.to_datetime_string()}."
        )

    @staticmethod
    def load_catalog_of_life_names(task: PythonOperator, remove_api_files: bool):
        local_zip_file = "COL_archive.zip"
        name_usage_file = "NameUsage.tsv"
        vernacular_file = "VernacularName.tsv"
        # download zip file from Catalog of Life
        if (OUTPUT_DIR / local_zip_file).exists():
            logger.info(
                f"{OUTPUT_DIR}/{local_zip_file} exists, so no Catalog of Life download."
            )
        else:
            # This is a static method so that it can be used to create preingestion
            # tasks for airflow. Unfortunately, that means it does not have access to
            # the delayed requester. So, we are just using requests for now.
            logger.info(
                f"Downloading Catalog of Life from "
                f"{COL_URL} to {OUTPUT_DIR}/{local_zip_file}."
            )
            with requests.get(COL_URL, stream=True) as response:
                response.raise_for_status()
                with open(OUTPUT_DIR / local_zip_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            logger.info(
                f"Saved Catalog of Life download: {OUTPUT_DIR}/{local_zip_file}"
            )
        # Extract specific files we need from the zip file
        if (OUTPUT_DIR / name_usage_file).exists() and (
            OUTPUT_DIR / vernacular_file
        ).exists():
            logger.info("No extract, both Catalog of Life tsv files exist.")
        else:
            with zipfile.ZipFile(OUTPUT_DIR / local_zip_file) as z:
                with open(OUTPUT_DIR / name_usage_file, "wb") as f:
                    f.write(z.read(name_usage_file))
                logger.info(f"Extracted raw file: {OUTPUT_DIR}/{name_usage_file}")
                with open(OUTPUT_DIR / vernacular_file, "wb") as f:
                    f.write(z.read(vernacular_file))
                logger.info(f"Extracted raw file: {OUTPUT_DIR}/{vernacular_file}")
        # set up for loading data
        pg = PostgresHook(
            default_statement_timeout=PostgresHook.get_execution_timeout(task)
        )
        COPY_SQL = (
            "COPY inaturalist.{} FROM STDIN "
            "DELIMITER E'\t' CSV HEADER QUOTE E'\b' NULL AS ''"
        )
        COUNT_SQL = "SELECT count(*) FROM inaturalist.{};"
        # upload vernacular names file to postgres
        pg.run_statement_timeout()
        pg.copy_expert(COPY_SQL.format("col_vernacular"), OUTPUT_DIR / vernacular_file)
        vernacular_records = pg.get_records(COUNT_SQL.format("col_vernacular"))
        if vernacular_records[0][0] == 0:
            raise AirflowNotFoundException("No Catalog of Life vernacular data loaded.")
        else:
            logger.info(
                f"Loaded {vernacular_records[0][0]} records from {vernacular_file}"
            )
        # upload name usage file to postgres
        pg.copy_expert(COPY_SQL.format("col_name_usage"), OUTPUT_DIR / name_usage_file)
        name_usage_records = pg.get_records(COUNT_SQL.format("col_name_usage"))
        if name_usage_records[0][0] == 0:
            raise AirflowNotFoundException("No Catalog of Life name usage data loaded.")
        else:
            logger.info(
                f"Loaded {name_usage_records[0][0]} records from {name_usage_file}"
            )
        # TO DO #917: save source files on s3?
        if remove_api_files:
            os.remove(OUTPUT_DIR / local_zip_file)
            os.remove(OUTPUT_DIR / vernacular_file)
            os.remove(OUTPUT_DIR / name_usage_file)
        return {
            "COL Name Usage Records": name_usage_records[0][0],
            "COL Vernacular Records": vernacular_records[0][0],
        }

    @staticmethod
    def create_preingestion_tasks():
        with TaskGroup(group_id="preingestion_tasks") as preingestion_tasks:
            check_for_file_updates = PythonOperator(
                task_id="check_for_file_updates",
                python_callable=INaturalistDataIngester.compare_update_dates,
                # Pass in the start date of the prior successful dag run
                # https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
                op_kwargs={
                    "last_success": "{{ prev_start_date_success }}",
                    "s3_keys": [
                        f"{file_name}.csv.gz" for file_name in SOURCE_FILE_NAMES
                    ],
                },
                doc_md="Check for iNaturalist files added to S3 since last load",
            )

            create_inaturalist_schema = PGExecuteQueryOperator(
                task_id="create_inaturalist_schema",
                sql=(SCRIPT_DIR / "create_schema.sql").read_text(),
                doc_md="Create temporary schema and license table",
                execution_timeout=timedelta(minutes=1),
            )

            load_catalog_of_life_names = PythonOperator(
                task_id="load_catalog_of_life_names",
                python_callable=INaturalistDataIngester.load_catalog_of_life_names,
                doc_md="Load vernacular taxon names from Catalog of Life",
                op_kwargs={
                    "remove_api_files": "{{ params.sql_rm_source_data_after_ingesting or var.json.SQL_RM_SOURCE_DATA_AFTER_INGESTION }}",
                },
                execution_timeout=timedelta(minutes=15),
            )

            (
                check_for_file_updates
                >> create_inaturalist_schema
                >> load_catalog_of_life_names
            )

        return preingestion_tasks

    @staticmethod
    def create_postingestion_tasks():
        with TaskGroup(group_id="postingestion_tasks") as postingestion_tasks:
            check_drop_parameter = ShortCircuitOperator(
                task_id="check_drop_parameter",
                doc_md="Skip post-ingestion if NOT sql_rm_source_data_after_ingesting.",
                op_args=[
                    "{{ params.sql_rm_source_data_after_ingesting }}",
                    "{{ var.json.SQL_RM_SOURCE_DATA_AFTER_INGESTION}}",
                ],
                python_callable=(lambda *x: any(x)),
                trigger_rule=TriggerRule.NONE_SKIPPED,
                # just skip the drop steps, not the final reporting step in the dag
                ignore_downstream_trigger_rules=False,
            )
            drop_inaturalist_schema = PGExecuteQueryOperator(
                task_id="drop_inaturalist_schema",
                sql="DROP SCHEMA IF EXISTS inaturalist CASCADE",
                doc_md="Drop iNaturalist source tables and their schema",
                execution_timeout=timedelta(minutes=10),
            )
            drop_loading_table = PythonOperator(
                task_id="drop_loading_table",
                python_callable=sql.drop_load_table,
                op_kwargs=LOADER_ARGS,
                doc_md="Drop the temporary (transformed) loading table",
                execution_timeout=timedelta(minutes=10),
            )
            (check_drop_parameter >> [drop_inaturalist_schema, drop_loading_table])
        return postingestion_tasks

    @staticmethod
    def create_ingestion_workflow():
        with TaskGroup(group_id="ingest_data") as ingest_data:
            preingestion_tasks = INaturalistDataIngester.create_preingestion_tasks()

            with TaskGroup(group_id="pull_image_data") as pull_data:
                for source_name in SOURCE_FILE_NAMES:
                    PGExecuteQueryOperator(
                        task_id=f"load_{source_name}",
                        sql=(SCRIPT_DIR / f"{source_name}.sql").read_text(),
                        doc_md=f"Load iNaturalist {source_name} from s3 to postgres",
                        execution_timeout=timedelta(minutes=30),
                    )

            with TaskGroup(group_id="load_image_data") as loader_tasks:
                # Using the existing set up, but the indexes on the temporary table
                # probably slows down the load a bit.
                create_loading_table = PythonOperator(
                    task_id="create_loading_table",
                    python_callable=sql.create_loading_table,
                    op_kwargs=LOADER_ARGS,
                    doc_md=(
                        "Create a temp table for ingesting data from inaturalist "
                        "source tables."
                    ),
                    execution_timeout=timedelta(minutes=1),
                )

                get_batches = PythonOperator(
                    task_id="get_batches",
                    python_callable=INaturalistDataIngester.get_batches,
                    op_kwargs={
                        "batch_length": 1_000_000,
                    },
                    execution_timeout=timedelta(minutes=1),
                )

                # In testing this locally with batch length 2_000_000, the longest full
                # iteration took 39 minutes, median was 18 minutes.
                load_transformed_data = PythonOperator.partial(
                    task_id="load_transformed_data",
                    python_callable=INaturalistDataIngester.load_transformed_data,
                    retries=0,
                    max_active_tis_per_dag=1,
                    op_kwargs={
                        "intermediate_table": XCOM_PULL_TEMPLATE.format(
                            create_loading_table.task_id, "return_value"
                        ),
                        "identifier": LOADER_ARGS["identifier"],
                    },
                    doc_md=(
                        "Load one batch of data from source tables to target table."
                    ),
                    # Use all of the available pool slots.
                    pool_slots=128,
                    # Default priority_weight is 1, higher numbers are more important.
                    priority_weight=0,
                    # Particularly towards the beginning there will be lots of
                    # of downstream / dependent tasks, and we don't want airflow to
                    # consider that in scheduling.
                    weight_rule="absolute",
                ).expand(
                    op_args=XComArg(get_batches, "return_value"),
                )

                consolidate_load_statistics = PythonOperator(
                    task_id="consolidate_load_statistics",
                    python_callable=INaturalistDataIngester.consolidate_load_statistics,
                    op_kwargs={
                        "all_results": load_transformed_data.output,
                    },
                    doc_md=(
                        "Total load counts across batches from load_transformed_data."
                    ),
                    retries=0,
                    trigger_rule=TriggerRule.NONE_SKIPPED,
                )
                (
                    create_loading_table
                    >> get_batches
                    >> load_transformed_data
                    >> consolidate_load_statistics
                )

            postingestion_tasks = INaturalistDataIngester.create_postingestion_tasks()

            (preingestion_tasks >> pull_data >> loader_tasks >> postingestion_tasks)

        # Reporting on the time it takes to load transformed data into the intermediate
        # table, clean it, and upsert it to the final target. This is not strictly
        # comparable to the time it takes to load from the s3 source.
        ingestion_metrics = {
            "duration": XCOM_PULL_TEMPLATE.format(
                consolidate_load_statistics.task_id, "duration"
            ),
            "record_counts_by_media_type": XCOM_PULL_TEMPLATE.format(
                consolidate_load_statistics.task_id, "return_value"
            ),
        }

        return ingest_data, ingestion_metrics
