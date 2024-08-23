import logging
from datetime import timedelta

from airflow.decorators import task
from airflow.models import BaseOperator
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.mappedoperator import MappedOperator
from airflow.providers.common.sql.hooks.sql import fetch_one_handler
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import (
    PostgresHook as UpstreamPostgresHook,
)

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID


# More on how Airflow timeouts work is in the docs here:
# https://airflow.apache.org/docs/apache-airflow/2.5.1/core-concepts/tasks.html#timeouts
# We set default task execution timeouts in common.constants.DAG_DEFAULT_ARGS
# https://airflow.apache.org/docs/apache-airflow/2.5.1/core-concepts/dags.html#default-arguments
# and for provider scripts, we set some timeouts in
# dags.providers.provider_workflows.PROVIDER_WORKFLOWS

logger = logging.getLogger(__name__)


# Some functions, like inaturalist, use "copy_expert" to bulk load data to a table.
# Right now, that is not using the timeout automagically.
# https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/_api/airflow/providers/postgres/hooks/postgres/index.html#airflow.providers.postgres.hooks.postgres.PostgresHook.copy_expert # noqa


RETURN_ROW_COUNT = lambda c: c.rowcount  # noqa: E731


def single_value(cursor):
    try:
        row = cursor.fetchone()
        return row[0]
    except Exception as e:
        raise ValueError("Unable to extract expected row data from cursor") from e


class PostgresHook(UpstreamPostgresHook):
    """
    PostgresHook that sets the database timeout on any query to match the airflow task
    execution timeout or a specific timeout for a particular run.

    default_statement_timeout: number of seconds postgres should wait before canceling
        the query (note: can override this by passing statement_timeout to the `run`
        method, but other methods like `get_records` which rely on `run` are not set up
        to pass an override timeout through to `run`. Not clear that it always works to
        have a `statement_timeout` that is longer than the airflow task
        `execution_timeout`.)
    see airflow.providers.postgres.hooks.postgres.PostgresHook for more on other params
    """

    def __init__(
        self,
        postgres_conn_id: str = POSTGRES_CONN_ID,
        default_statement_timeout: float = None,
        *args,
        **kwargs,
    ) -> None:
        self.default_statement_timeout = default_statement_timeout
        if default_statement_timeout is None:
            self.default_statement_timeout = DAG_DEFAULT_ARGS[
                "execution_timeout"
            ].total_seconds()
        self.postgres_conn_id = postgres_conn_id
        if postgres_conn_id is None:
            self.postgres_conn_id = POSTGRES_CONN_ID
        super().__init__(self.postgres_conn_id, *args, **kwargs)

    def run(
        self,
        sql,
        statement_timeout: float = None,
        autocommit=False,
        parameters=None,
        handler: callable = fetch_one_handler,
        *args,
        **kwargs,
    ):
        statement_timeout = statement_timeout or self.default_statement_timeout

        if statement_timeout:
            timeout_sql = self.get_pg_timeout_sql(statement_timeout)
            if isinstance(sql, list):
                sql = [timeout_sql, *sql]
            else:
                sql = f"{timeout_sql} {sql}"
        return super().run(sql, autocommit, parameters, handler)

    @staticmethod
    def get_execution_timeout(task: BaseOperator | MappedOperator = None) -> float:
        """
        Pull execution timeout from airflow task and format it for the hook, i.e.
        number of seconds. Use the task execution timeout, if available. If not, take
        the DAG execution timeout, if that's not available, return 0 for no timeout.

        If the task falls through the cracks between functions and 'None' is passed
        instead, return the common.constants dag default task timeout, and note the
        decision in the log.
        """
        universal_default = DAG_DEFAULT_ARGS["execution_timeout"].total_seconds()
        if task is None:
            logger.warning(
                f"No task supplied, using default timeout of {universal_default}s"
            )
            return universal_default

        # DAG-level default task execution timeout, which may come from
        # common.constants.DAG_DEFAULT_ARGS["execution_timeout"]
        # or by over-ridden for a specific DAG as in image expiration.
        # https://github.com/WordPress/openverse-catalog/blob/main/catalog/dags/database/image_expiration_workflow.py#L24
        dag_default_timeout = getattr(task.dag, "default_args", {}).get(
            "execution_timeout"
        )

        # explicitly specified with the task
        if isinstance(task, BaseOperator):
            task_timeout = task._BaseOperator__init_kwargs.get("execution_timeout")
        elif isinstance(task, MappedOperator):
            task_timeout = task.partial_kwargs.get("execution_timeout")
        else:
            task_timeout = None

        # Prefer the most immediately specified. Here "None" means not specified and
        # results in the universal default timeout, while timedelta(seconds=0) which is
        # not None but also falsey means "Set no timeout at all."
        if task_timeout is not None:
            return task_timeout.total_seconds()
        elif dag_default_timeout is not None:
            return dag_default_timeout.total_seconds()
        else:
            return universal_default

    @staticmethod
    def get_pg_timeout_sql(statement_timeout: float) -> str:
        return f"SET statement_timeout TO '{statement_timeout}s';"

    def run_statement_timeout(self):
        """
        Pass an empty SQL statement to the regular run command so that only the
        timeout setting gets run.
        """
        self.run("")


class PGExecuteQueryOperator(SQLExecuteQueryOperator):
    """
    SQL Operator that sets the database statement timeout to match the airflow task
    execution timeout. execution_timeout is a standard Airflow parameter that should be
    in the form of `datetime.timedelta`. See SQLExecuteQueryOperator for more on other
    params.
    """

    def __init__(
        self,
        *,
        postgres_conn_id: str = None,
        execution_timeout: timedelta = None,
        **kwargs,
    ) -> None:
        self.statement_timeout = None
        if execution_timeout:
            self.statement_timeout = execution_timeout.total_seconds()
        self.postgres_conn_id = postgres_conn_id or kwargs.get("conn_id")
        super().__init__(**kwargs)

    def get_db_hook(self):
        return PostgresHook(
            default_statement_timeout=self.statement_timeout,
            postgres_conn_id=self.postgres_conn_id,
            **self.hook_params,
        )


@task
def run_sql(
    postgres_conn_id: str,
    sql_template: str,
    task: AbstractOperator = None,
    timeout: float = None,
    handler: callable = RETURN_ROW_COUNT,
    **kwargs,
):
    """
    Run an SQL query with the given template and parameters. Any kwargs handed
    into the function outside of those defined will be passed into the template
    `.format` call.
    """
    query = sql_template.format(**kwargs)

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
    )

    return postgres.run(query, handler=handler)
