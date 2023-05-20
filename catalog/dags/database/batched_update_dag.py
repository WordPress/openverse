"""
Batched Update DAG

TODO: This should include an example DagRun configuration which shows all possible
configs, including optional ones, and then shows what the queries will look like.

An example dag_run conf for this DAG currently:

```
{
    "query_id": "my_query",
    "table_name": "image",
    "select_query": "WHERE provider='stocksnap'",
    "update_query": "SET standardized_popularity=standardized_image_popularity(image.provider, image.meta_data)",
    "batch_size": 10,
    "dry_run": false
}
```
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.models.abstractoperator import AbstractOperator
from airflow.utils.trigger_rule import TriggerRule

from common import slack
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.loader.sql import TABLE_NAMES
from common.sql import PostgresHook


logger = logging.getLogger(__name__)


# TODO: Refactor into multiple files


@dataclass
class BatchedUpdateConfig:
    """ "
    TODO: docstr
    """

    query_id: str
    table_name: str
    select_query: str
    update_query: str
    batch_size: int

    dry_run: bool = True
    select_timeout: timedelta = timedelta(hours=6)
    update_batch_timeout: timedelta = timedelta(hours=1)
    dagrun_timeout: timedelta = timedelta(days=31)
    temp_table_name: str | None = None

    def __post_init__(self):
        self.temp_table_name = f"rows_to_update_{self.query_id}"


CREATE_TEMP_TABLE_QUERY = """
    CREATE TABLE {temp_table_name} AS
    SELECT ROW_NUMBER() OVER() row_id, identifier
    FROM {table_name}
    {select_query}
    AND updated_on < NOW();
    """
CREATE_TEMP_TABLE_INDEX_QUERY = "CREATE INDEX ON {temp_table_name}(row_id)"
UPDATE_BATCH_QUERY = """
    UPDATE {table_name}
    {update_query}
    WHERE identifier in (
        SELECT identifier FROM {temp_table_name}
        WHERE row_id >= {batch_start} AND row_id < {batch_end}
        FOR UPDATE SKIP LOCKED
    );
    """
DROP_TABLE_QUERY = "DROP TABLE IF EXISTS {temp_table_name} CASCADE;"
RETURN_ROW_COUNT = lambda c: c.rowcount  # noqa: E731


@task
def run_sql(
    config,
    sql_template,
    postgres_conn_id=POSTGRES_CONN_ID,
    task: AbstractOperator = None,
    **kwargs,
):
    query = sql_template.format(**asdict(config), **kwargs)
    if config.dry_run:
        logger.info(
            "This is a dry run: no SQL will be executed. To perform the updates,"
            " rerun the DAG with the conf option `'dry_run': false`."
        )
        logger.info(query)
        return

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    return postgres.run(query, handler=RETURN_ROW_COUNT)


@task
def validate_configuration(dag_run=None):
    """
    TODO:
    - Fix the error messages (supply examples, adjust formatting)
    - Add option for overriding timeouts for the select and update batch tasks
    """
    if dag_run is None or dag_run.conf is None:
        # This should not happen
        raise AirflowException("Missing DagRun configuration")
    errors = []

    query_id = dag_run.conf.get("query_id")
    if not query_id or not isinstance(query_id, str):
        errors.append(
            "Please supply a `query_id`, a string which uniquely identifies your"
            " update query. It will be used as a suffix in the temp table."
        )

    table_name = dag_run.conf.get("table_name")
    if not table_name or table_name not in TABLE_NAMES.values():
        options = ", ".join(TABLE_NAMES.values())
        errors.append(
            f"Please supply a valid table name to update. Valid options are:"
            f" {options}."
        )

    select_query = dag_run.conf.get("select_query")
    # TODO: Maybe we should also allow it to start with the various join statements
    if not select_query or not select_query.startswith("WHERE"):
        errors.append(
            "Please supply a value for `select_query` which selects the rows you would."
            " like to update. The query should begin with `WHERE`."
        )  # TODO: Example

    update_query = dag_run.conf.get("update_query")
    if not update_query or not update_query.startswith("SET"):
        errors.append(
            "Please supply a value for `update_query` which does the update. The query"
            " should start with `SET`."
        )

    batch_size = dag_run.conf.get("batch_size")
    # TODO: Default batch size instead of requiring it?
    if not batch_size or not isinstance(batch_size, int):
        errors.append("Please supply an integer value for `batch_size`.")

    dry_run = dag_run.conf.get("dry_run", True)
    if not isinstance(dry_run, bool):
        # TODO help text for dry_run
        errors.append("Invalid value for `dry_run`")

    if errors:
        msg = "\n".join(errors)
        raise ValueError(msg)

    return BatchedUpdateConfig(
        query_id=query_id,
        table_name=table_name,
        select_query=select_query,
        update_query=update_query,
        batch_size=batch_size,
        dry_run=dry_run,
    )


@task
def notify_slack(text: str) -> None:
    # TODO Set constants
    slack.send_message(
        text,
        username="BATCHED UPDATE",
        # icon_emoji=constants.SLACK_ICON,
        dag_id="batched_update",
    )


@task
def make_batches(total, config):
    if config.dry_run:
        # TODO: should we do something else here? The issue is that in a dry run, we
        # didn't actually build the temp table so we don't know the `total` number of
        # records we're updating and can't really make batches.
        logger.info("Returning a sample batch for the dry run.")
        return [{"batch_start": 1, "batch_end": config.batch_size}]

    return [
        {"batch_start": i, "batch_end": min(i + config.batch_size, total + 1)}
        for i in range(1, total + 1, config.batch_size)
    ]


@dag(
    dag_id="batched_update",
    schedule=None,
    start_date=datetime(2023, 5, 1),
    tags=["database"],
    max_active_tasks=1,  # Ensures that the batches only run one at a time
    max_active_runs=10,  # TODO make this a larger number?
    dagrun_timeout=timedelta(days=30 * 3),  # 3 months TODO re-evaluate
    doc_md=__doc__,
    default_args={
        # TODO: default task timeouts
        **DAG_DEFAULT_ARGS,
        "retries": 0,
    },
    render_template_as_native_obj=True,
)
def batched_update():
    # TODO: Why is this set as explicitly upstream of all tasks.
    # It makes the graph look awful.
    config = validate_configuration()

    # TODO. If we add a task at the beginning to get MAX_TIMESTAMP, then we can use
    # max timestamp in the initial SELECT but ALSO in the update, like we add it to the
    # WHERE so that we don't bother trying to update things here.

    # TODO: If select_rows_to_update gets 0 rows, finish early
    # TODO: If select_rows_to_update returns None, there was a problem -- fail the DAG
    select_rows_to_update = run_sql.override(
        task_id="select_rows_to_update",
        # TODO: How do we override the timeout here? We cannot set it to
        # config.select_timeout because config is an XComArg. I don't see a way to
        # access a member of the dataclass here. This also did not work when I
        # modified the config task to return a simple dictionary instead of a
        # dataclass; the value for `select_timeout` is still an XComArg.
        # execution_timeout=config['select_timeout']
    )(config=config, sql_template=CREATE_TEMP_TABLE_QUERY)

    config >> select_rows_to_update

    create_index = run_sql.override(task_id="create_index")(
        config=config, sql_template=CREATE_TEMP_TABLE_INDEX_QUERY
    )

    # TODO: Because we set max_active_tasks to one, we actually risk this task not
    # getting scheduled until after the update tasks all finish. Maybe set it
    # upstream of update_batches
    notify_before_update = notify_slack.override(task_id="notify_before_update")(
        f"Preparing to update {select_rows_to_update} rows."
    )

    select_rows_to_update >> [create_index, notify_before_update]

    # TODO: The batches are running sequentially (rather than concurrently) because I
    # set the `max_active_tasks` to 1. We could adjust that?
    # However there's also a problem which is that the whole DAG doesn't fail as soon as
    # one task fails. If a batch fails, the others will all keep trying to run.
    # This can't be addressed by a trigger rule because the dynamic tasks aren't
    # upstream of each other.
    update_batches = (
        run_sql.override(
            task_id="update_batches",
        )
        .partial(config=config, sql_template=UPDATE_BATCH_QUERY)
        .expand_kwargs(make_batches(select_rows_to_update, config))
    )

    # TODO: How to enforce that create_index runs before make_batches?
    create_index >> update_batches

    notify_updated_count = notify_slack.override(task_id="notify_updated_count")(
        f"Updated {update_batches} records."
    )

    drop_temporary_table = run_sql.override(
        task_id="drop_temp_table", trigger_rule=TriggerRule.ALL_DONE
    )(config=config, sql_template=DROP_TABLE_QUERY)

    update_batches >> [notify_updated_count, drop_temporary_table]


batched_update()
