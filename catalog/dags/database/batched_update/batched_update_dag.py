"""
Batched Update DAG

This DAG is used to run a batched SQL update on a media table in the Catalog database.
It is automatically triggered by the `popularity_refresh` DAGs to refresh popularity
data using newly calculated constants, but can also be triggered manually with custom
SQL operations.

The DAG must be run with a valid dag_run configuration specifying the SQL commands to
be run. The DAG will then split the rows to be updated into batches, and report to Slack
when all batches have been updated. It handles all deadlocking and timeout concerns,
ensuring that the provided SQL is run without interfering with ingestion. For more
information, see the implementation plan:
https://docs.openverse.org/projects/proposals/popularity_optimizations/20230420-implementation_plan_popularity_optimizations.html#special-considerations-avoiding-deadlocks-and-timeouts

By default the DAG will run as a dry_run, logging the generated SQL but not actually
running it. To actually perform the update, the `dry_run` parameter must be
explicitly set to `false` in the configuration.

Required Dagrun Configuration parameters:

* query_id:     a string identifier which will be appended to temporary table used in
                the update
* table_name:   the name of the table to update. Must be a valid media table
* select_query: a SQL `WHERE` clause used to select the rows that will be updated
* update_query: the SQL `UPDATE` expression to be run on all selected rows

Optional Arguments:

* dry_run: bool, whether to actually run the generated SQL. False by default.
* batch_size: int number of records to process in each batch. By default, 10_000
* update_timeout: int number of seconds to run an individual batch update before timing
                  out. By default, 3600 (or one hour)

An example dag_run configuration used to set the thumbnails of all Flickr images to
null would look like this:

```
{
    "query_id": "my_flickr_query",
    "table_name": "image",
    "select_query": "WHERE provider='flickr'",
    "update_query": "SET thumbnail=null",
    "batch_size": 10,
    "dry_run": false
}
```
"""


import logging

from airflow.decorators import dag
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

from common.constants import AUDIO, DAG_DEFAULT_ARGS, MEDIA_TYPES
from database.batched_update import constants
from database.batched_update.batched_update import notify_slack, run_sql, update_batches


logger = logging.getLogger(__name__)


@dag(
    dag_id=constants.DAG_ID,
    schedule=None,
    start_date=constants.START_DATE,
    tags=["database"],
    # This allows for multiple concurrent batched updates to run, for example popularity
    # refreshes for each provider
    max_active_runs=10,
    dagrun_timeout=constants.DAGRUN_TIMEOUT,
    doc_md=__doc__,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
    },
    render_template_as_native_obj=True,
    params={
        "query_id": Param(
            default="",
            type="string",
            description=(
                "A string which will be appended to the temp table created"
                " during the update, in order to uniquely identify your query."
            ),
        ),
        "table_name": Param(
            default=AUDIO,
            enum=MEDIA_TYPES,
            description=("The name of the media table to be updated."),
        ),
        "select_query": Param(
            default="WHERE...",
            type="string",
            description=(
                "The `WHERE` clause of a query that selects all the rows to"
                " be updated."
            ),
            pattern="^WHERE",
        ),
        "update_query": Param(
            default="SET...",
            type="string",
            description=(
                "The part of the SQL `UPDATE` command, beginning with `SET`, that"
                " will be run for each batch."
            ),
            pattern="^SET",
        ),
        "batch_size": Param(
            default=constants.DEFAULT_BATCH_SIZE,
            type="integer",
            description=("The number of records to update per batch."),
        ),
        "update_timeout": Param(
            default=constants.DEFAULT_UPDATE_BATCH_TIMEOUT,
            type="integer",
            description=(
                "Integer number of seconds giving the maximum length of time it "
                "should take for a single batch to be updated."
            ),
        ),
        "dry_run": Param(
            default=True,
            type="boolean",
            description=(
                "When True, the SQL commands will not actually be run"
                " but only logged."
            ),
        ),
    },
)
def batched_update():
    select_rows_to_update = run_sql.override(
        task_id="select_rows_to_update", execution_timeout=constants.SELECT_TIMEOUT
    )(
        sql_template=constants.CREATE_TEMP_TABLE_QUERY,
        dry_run="{{ params.dry_run }}",
        query_id="{{ params.query_id }}",
        table_name="{{ params.table_name }}",
        select_query="{{ params.select_query }}",
    )

    create_index = run_sql.override(task_id="create_index")(
        sql_template=constants.CREATE_TEMP_TABLE_INDEX_QUERY,
        dry_run="{{ params.dry_run }}",
        query_id="{{ params.query_id }}",
    )

    notify_before_update = notify_slack.override(task_id="notify_before_update")(
        text=f"Preparing to update {select_rows_to_update} rows for update:"
        " {{ params.query_id }}",
        dry_run="{{ params.dry_run}}",
    )

    select_rows_to_update >> [create_index, notify_before_update]

    perform_batched_update = update_batches.override(
        execution_timeout=constants.UPDATE_TIMEOUT
    )(
        expected_row_count=select_rows_to_update,
        batch_size="{{ params.batch_size }}",
        dry_run="{{ params.dry_run }}",
        table_name="{{ params.table_name }}",
        query_id="{{ params.query_id }}",
        update_query="{{ params.update_query }}",
        update_timeout="{{ params.update_timeout }}",
    )

    create_index >> perform_batched_update

    notify_updated_count = notify_slack.override(task_id="notify_updated_count")(
        text=f"Updated {perform_batched_update} records for update:"
        " {{ params.query_id }}",
        dry_run="{{ params.dry_run}}",
    )

    # The temporary table is only dropped if all updates were successful; this
    # prevents needing to rebuild a potentially expensive table when
    # retrying the DAG.
    drop_temporary_table = run_sql.override(
        task_id="drop_temp_table",
    )(
        sql_template=constants.DROP_TABLE_QUERY,
        dry_run="{{ params.dry_run }}",
        query_id="{{ params.query_id }}",
    )

    # If there was an error, notify to Slack that the temporary table must be
    # dropped manually or the DAG retried.
    notify_failure = notify_slack.override(
        task_id="notify_failure", trigger_rule=TriggerRule.ONE_FAILED
    )(
        text="Update {{ params.query_id }} failed: retry the DAG or manually drop the"
        " temp table.",
        dry_run="{{ params.dry_run}}",
    )

    perform_batched_update >> [
        notify_updated_count,
        drop_temporary_table,
        notify_failure,
    ]


batched_update()
