"""
# Provider DAG Factory
This file contains two factory functions which generate the bulk of our
provider workflow DAGs. These DAGs pull data in from a particular provider,
and produce one or several TSVs of the results.

The "simple" (non-partitioned) DAG also loads the TSVs into the catalog database.

The loading step takes the media data saved locally in TSV files, cleans it using an
intermediate database table, and saves the cleaned-up data into the main database
(also called upstream or Openledger).

In production,"locally" means on AWS EC2 instance that runs the Apache Airflow
webserver. Storing too much data there is dangerous, because if ingestion to the
database breaks down, the disk of this server gets full, and breaks all
Apache Airflow operations.

As a first step, the loader portion of the DAG saves the data gathered by
Provider API Scripts to S3 before attempting to load it to PostgreSQL, and delete
it from disk if saving to S3 succeeds, even if loading to PostgreSQL fails.

This way, we can delete data from the EC2 instance to open up disk space without
the possibility of losing that data altogether. This will allow us to recover if
we lose data from the DB somehow, because it will all be living in S3.
It's also a prerequisite to the long-term plan of saving data only to S3
(since saving it to the EC2 disk is a source of concern in the first place).

This is one step along the path to avoiding saving data on the local disk at all.
It should also be faster to load into the DB from S3, since AWS RDS instances
provide special optimized functionality to load data from S3 into tables in the DB.

Loading the data into the Database is a two-step process: first, data is saved
to the intermediate table. Any items that don't have the required fields
(media url, license, foreign landing url and foreign id), and duplicates as
determined by combination of provider and foreign_id are deleted.
Then the data from the intermediate table is upserted into the main database.
If the same item is already present in the database, we update its information
with newest (non-null) data, and merge any metadata or tags objects to preserve all
previously downloaded data, and update any data that needs updating
(eg. popularity metrics).

Provider workflows which extend the ProviderDataIngester class support a few DagRun
configuration variables:

* `skip_ingestion_errors`: When set to true, errors encountered during ingestion will
be caught to allow ingestion to continue. The `pull_data` task will still fail when
ingestion is complete, and report a summary of all encountered errors. By default
`skip_ingestion_errors` is False.
* `initial_query_params`: An optional dict of query parameters with which to begin
ingestion. This allows a user to manually force ingestion to resume from a particular
batch, for example when retrying after an error.

You can find more background information on the loading process in the following
issues and related PRs:

- [[Feature] More sophisticated merging of columns in PostgreSQL when upserting](
https://github.com/creativecommons/cccatalog/issues/378)

- [DB Loader DAG should write to S3 as well as PostgreSQL](
https://github.com/creativecommons/cccatalog/issues/333)

- [DB Loader should take data from S3, rather than EC2 to load into PostgreSQL](
https://github.com/creativecommons/cccatalog/issues/334)
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Sequence

from airflow import DAG
from airflow.models.baseoperator import cross_downstream
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule
from common.constants import DAG_DEFAULT_ARGS, XCOM_PULL_TEMPLATE
from common.loader import loader, reporting, s3, sql
from providers.factory_utils import (
    date_partition_for_prefix,
    generate_tsv_filenames,
    pull_media_wrapper,
)


logger = logging.getLogger(__name__)


DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
AWS_CONN_ID = os.getenv("AWS_CONN_ID", "no_aws_conn_id")
OPENVERSE_BUCKET = os.getenv("OPENVERSE_BUCKET")
OUTPUT_DIR_PATH = os.path.realpath(os.getenv("OUTPUT_DIR", "/tmp/"))
DATE_RANGE_ARG_TEMPLATE = "{{{{ macros.ds_add(ds, -{}) }}}}"
DATE_PARTITION_ARG_TEMPLATE = "{media_type}/{provider_name}/{{{{ date_partition_for_prefix(dag.schedule_interval, dag_run.logical_date) }}}}"  # noqa


def create_provider_api_workflow(
    dag_id: str,
    ingestion_callable: Callable,
    default_args: Optional[Dict] = None,
    start_date: datetime = datetime(1970, 1, 1),
    max_active_runs: int = 1,
    max_active_tasks: int = 1,
    schedule_string: str = "@daily",
    dated: bool = True,
    day_shift: int = 0,
    pull_timeout: timedelta = timedelta(hours=12),
    load_timeout: timedelta = timedelta(hours=1),
    doc_md: Optional[str] = "",
    media_types: Sequence[str] = ("image",),
    create_preingestion_tasks: Optional[Callable] = None,
    create_postingestion_tasks: Optional[Callable] = None,
):
    """
    This factory method instantiates a DAG that will run the given
    `main_function`.

    Required Arguments:

    dag_id:             string giving a unique id of the DAG to be created.
    ingestion_callable: python function to be run, or a ProviderDataIngester class
                        whose `ingest_records` method is to be run. If the optional
                        argument `dated` is True, then the function must take a
                        single parameter (date) which will be a string of
                        the form 'YYYY-MM-DD'.

    Optional Arguments:

    default_args:      dictionary which is passed to the airflow.dag.DAG
                       __init__ method and used to optionally override the
                       DAG_DEFAULT_ARGS.
    start_date:        datetime.datetime giving the first valid execution
                       date of the DAG.
    max_active_runs:   integer that sets the number of dagruns for this DAG
                       which can be run in parallel.
    max_active_tasks:  integer that sets the number of tasks which can
                       run simultaneously for this DAG.
                       It's important to keep the rate limits of the
                       Provider API in mind when setting this parameter.
    schedule_string:   string giving the schedule on which the DAG should
                       be run.  Passed to the airflow.dag.DAG __init__
                       method.
    dated:             boolean giving whether the `main_function` takes a
                       string parameter giving a date (i.e., the date for
                       which data should be ingested).
    day_shift:         integer giving the number of days before the
                       current execution date the `main_function` should
                       be run (if `dated=True`).
    pull_timeout:      datetime.timedelta giving the amount of time a given data
                       pull may take.
    load_timeout:      datetime.timedelta giving the amount of time a given load_data
                       task may take.
    doc_md:            string which should be used for the DAG's documentation markdown
    media_types:       list describing the media type(s) that this provider handles
                       (e.g. `["audio"]`, `["image", "audio"]`, etc.)
    create_preingestion_tasks and create_postingestion_tasks: callable which creates a
                        task or task group to be run before or after (respectively) the
                        rest of the provider workflow. Loading and dropping temporary
                        tables is one example.
    """
    default_args = {**DAG_DEFAULT_ARGS, **(default_args or {})}
    media_type_name = "mixed" if len(media_types) > 1 else media_types[0]
    provider_name = dag_id.replace("_workflow", "")
    identifier = f"{provider_name}_{{{{ ts_nodash }}}}"

    dag = DAG(
        dag_id=dag_id,
        default_args={**default_args, "start_date": start_date},
        max_active_tasks=max_active_tasks,
        max_active_runs=max_active_runs,
        start_date=start_date,
        schedule_interval=schedule_string,
        catchup=dated,  # catchup is turned on for dated DAGs to allow backfilling
        doc_md=doc_md,
        tags=["provider"] + [f"provider: {media_type}" for media_type in media_types],
        render_template_as_native_obj=True,
        user_defined_macros={"date_partition_for_prefix": date_partition_for_prefix},
    )

    with dag:
        ingestion_kwargs = {
            "ingestion_callable": ingestion_callable,
            "media_types": media_types,
        }
        if dated:
            ingestion_kwargs["args"] = [DATE_RANGE_ARG_TEMPLATE.format(day_shift)]

        generate_filenames = PythonOperator(
            task_id=f"generate_{media_type_name}_filename",
            python_callable=generate_tsv_filenames,
            op_kwargs=ingestion_kwargs,
        )

        pull_data = PythonOperator(
            task_id=f"pull_{media_type_name}_data",
            python_callable=pull_media_wrapper,
            op_kwargs={
                **ingestion_kwargs,
                # Note: this is assumed to match the order of media_types exactly
                "tsv_filenames": [
                    XCOM_PULL_TEMPLATE.format(
                        generate_filenames.task_id, f"{media_type}_tsv"
                    )
                    for media_type in media_types
                ],
            },
            depends_on_past=False,
            execution_timeout=pull_timeout,
            # If the data pull fails, we want to load all data that's been retrieved
            # thus far before we attempt again
            retries=0,
        )

        load_tasks = []
        record_counts_by_media_type: reporting.MediaTypeRecordMetrics = {}
        for media_type in media_types:
            with TaskGroup(group_id=f"load_{media_type}_data") as load_data:
                create_loading_table = PythonOperator(
                    task_id="create_loading_table",
                    python_callable=sql.create_loading_table,
                    op_kwargs={
                        "postgres_conn_id": DB_CONN_ID,
                        "identifier": identifier,
                        "media_type": media_type,
                    },
                    trigger_rule=TriggerRule.NONE_SKIPPED,
                    doc_md="Create a temporary loading table for "
                    f"ingesting {media_type} data from a TSV",
                )
                copy_to_s3 = PythonOperator(
                    task_id="copy_to_s3",
                    python_callable=s3.copy_file_to_s3,
                    op_kwargs={
                        "tsv_file_path": XCOM_PULL_TEMPLATE.format(
                            generate_filenames.task_id, f"{media_type}_tsv"
                        ),
                        "s3_bucket": OPENVERSE_BUCKET,
                        "s3_prefix": DATE_PARTITION_ARG_TEMPLATE.format(
                            media_type=media_type,
                            provider_name=provider_name,
                        ),
                        "aws_conn_id": AWS_CONN_ID,
                    },
                    trigger_rule=TriggerRule.NONE_SKIPPED,
                )
                load_from_s3 = PythonOperator(
                    task_id="load_from_s3",
                    execution_timeout=load_timeout,
                    retries=1,
                    python_callable=loader.load_from_s3,
                    op_kwargs={
                        "bucket": OPENVERSE_BUCKET,
                        "key": XCOM_PULL_TEMPLATE.format(copy_to_s3.task_id, "s3_key"),
                        "postgres_conn_id": DB_CONN_ID,
                        "media_type": media_type,
                        "tsv_version": XCOM_PULL_TEMPLATE.format(
                            copy_to_s3.task_id, "tsv_version"
                        ),
                        "identifier": identifier,
                    },
                )
                drop_loading_table = PythonOperator(
                    task_id="drop_loading_table",
                    python_callable=sql.drop_load_table,
                    op_kwargs={
                        "postgres_conn_id": DB_CONN_ID,
                        "identifier": identifier,
                        "media_type": media_type,
                    },
                    trigger_rule=TriggerRule.ALL_DONE,
                )
                [create_loading_table, copy_to_s3] >> load_from_s3
                load_from_s3 >> drop_loading_table

                record_counts_by_media_type[media_type] = XCOM_PULL_TEMPLATE.format(
                    load_from_s3.task_id, "return_value"
                )
                load_tasks.append(load_data)

        report_load_completion = PythonOperator(
            task_id="report_load_completion",
            python_callable=reporting.report_completion,
            op_kwargs={
                "provider_name": provider_name,
                "duration": XCOM_PULL_TEMPLATE.format(pull_data.task_id, "duration"),
                "record_counts_by_media_type": record_counts_by_media_type,
                "dated": dated,
                "date_range_start": "{{ data_interval_start | ds }}",
                "date_range_end": "{{ data_interval_end | ds }}",
            },
            trigger_rule=TriggerRule.ALL_DONE,
        )

        generate_filenames >> pull_data >> load_tasks >> report_load_completion

        if create_preingestion_tasks:
            preingestion_tasks = create_preingestion_tasks()
            preingestion_tasks >> pull_data

        if create_postingestion_tasks:
            postingestion_tasks = create_postingestion_tasks()
            pull_data >> postingestion_tasks

    return dag


def create_day_partitioned_ingestion_dag(
    dag_id: str,
    main_function: Callable,
    reingestion_day_list_list: list[list[int]],
    start_date: datetime = datetime(1970, 1, 1),
    max_active_runs: int = 1,
    max_active_tasks: int = 1,
    default_args: Optional[Dict] = None,
    dagrun_timeout: timedelta = timedelta(hours=23),
    ingestion_task_timeout: timedelta = timedelta(hours=2),
):
    """
    Given a `main_function` and `reingestion_day_list_list`, this
    factory method instantiates a DAG that will run the given
    `main_function`, parameterized by a number of dates, whose
    calculation is described below.

    Required Arguments:

    dag_id:                     string giving a unique id of the DAG to
                                be created.
    main_function:              python function to be run. The
                                function must take a single parameter
                                (date) which will be a string of the
                                form 'YYYY-MM-DD'.
    reingestion_day_list_list:  list of lists of integers. It gives the
                                set of days before the current execution
                                date of the DAG for which the
                                `main_function` should be run, and
                                describes how the calls to the function
                                should be prioritized.

    Optional Arguments:

    start_date:              datetime.datetime giving the
                             first valid execution_date of the DAG.
    max_active_tasks:             integer that sets the number of tasks which
                             can run simultaneously for this DAG. It's
                             important to keep the rate limits of the
                             Provider API in mind when setting this
                             parameter.
    default_args:            dictionary which is passed to the
                             airflow.dag.DAG __init__ method and used to
                             optionally override the DAG_DEFAULT_ARGS.
    dagrun_timeout:          datetime.timedelta giving the total amount
                             of time a given dagrun may take.
    ingestion_task_timeout:  datetime.timedelta giving the amount of
                             time a call to the `main_function` is
                             allowed to take.

    Calculation of ingestion dates:

    The `reingestion_day_list_list` should have the form
        [
            [int, ..., int],
            [int, ..., int],
            ...,
            [int, ..., int]
        ]
    It's not necessary for the inner lists to be the same length. The
    DAG instantiated by this factory method will first run the
    `main_function` for the current execution_date, then for the current
    date minus the number of days given by integers in the first list
    (in an arbitrary order, and possibly in parallel if so configured),
    then for the dates calculated from the second list, and so on.  For
    example, given the `reingestion_day_list_list`
        [
            [1, 2, 3],
            [8, 13, 18],
            [28, 38, 48]
        ],
    and assuming the current execution date is 2020-01-01, the
    instantiated dag will run the `main_function` with the parameters
        [
            ['2020-01-01'],
            ['2019-12-31', 2019-12-30', '2019-12-29'],
            ['2019-12-24', 2019-12-19', '2019-12-14'],
            ['2019-12-04', 2019-11-24', '2019-11-14']
        ].
    The order of the inner lists gives the order in which sets of dates
    may be run.  The order within the inner lists is not relevant.  The
    size of the inner lists does *not* set the number of simultaneous
    executions of the `main_function` allowed; that is set by the
    `max_active_tasks` parameter.
    """
    default_args = {**DAG_DEFAULT_ARGS, **(default_args or {})}
    dag = DAG(
        dag_id=dag_id,
        default_args={**default_args, "start_date": start_date},
        max_active_tasks=max_active_tasks,
        max_active_runs=max_active_runs,
        dagrun_timeout=dagrun_timeout,
        schedule_interval="@daily",
        start_date=start_date,
        catchup=False,
        tags=["provider-reingestion"],
    )
    with dag:
        ingest_operator_list_list = _build_ingest_operator_list_list(
            reingestion_day_list_list, main_function, ingestion_task_timeout
        )
        for i in range(len(ingest_operator_list_list) - 1):
            wait_operator = EmptyOperator(
                task_id=f"wait_L{i}", trigger_rule=TriggerRule.ALL_DONE
            )
            cross_downstream(ingest_operator_list_list[i], [wait_operator])
            wait_operator >> ingest_operator_list_list[i + 1]
        ingest_operator_list_list[-1]

    return dag


def _build_ingest_operator_list_list(
    reingestion_day_list_list, main_function, ingestion_task_timeout
):
    if reingestion_day_list_list[0] != [0]:
        reingestion_day_list_list = [[0]] + reingestion_day_list_list
    return [
        [
            PythonOperator(
                task_id=f"ingest_{d}",
                python_callable=main_function,
                op_args=[DATE_RANGE_ARG_TEMPLATE.format(d)],
                execution_timeout=ingestion_task_timeout,
                depends_on_past=False,
            )
            for d in L
        ]
        for L in reingestion_day_list_list
    ]
