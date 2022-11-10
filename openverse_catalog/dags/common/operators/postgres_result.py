from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from psycopg2.sql import SQL, Identifier


if TYPE_CHECKING:
    from airflow.utils.context import Context


class PostgresResultOperator(PostgresOperator):
    """
    Override for the PostgresOperator which is functionally identical except that a
    handler can be specified for the PostgresHook. The value(s) accumulated from the
    run function will then be pushed as an XCom.
    """

    def __init__(
        self,
        *,
        sql: str | list[str],
        handler: Callable,
        postgres_conn_id: str = "postgres_default",
        autocommit: bool = False,
        parameters: Mapping | Iterable | None = None,
        database: str | None = None,
        runtime_parameters: Mapping | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            sql=sql,
            postgres_conn_id=postgres_conn_id,
            autocommit=autocommit,
            parameters=parameters,
            database=database,
            runtime_parameters=runtime_parameters,
            **kwargs,
        )
        self.handler = handler

    def execute(self, context: "Context"):
        """
        This almost exactly mirrors PostgresOperator::execute, except that it allows
        passing a handler into the hook.
        """
        self.hook = PostgresHook(
            postgres_conn_id=self.postgres_conn_id, schema=self.database
        )
        if self.runtime_parameters:
            final_sql = []
            sql_param = {}
            for param in self.runtime_parameters:
                set_param_sql = f"SET {{}} TO %({param})s;"
                dynamic_sql = SQL(set_param_sql).format(Identifier(f"{param}"))
                final_sql.append(dynamic_sql)
            for param, val in self.runtime_parameters.items():
                sql_param.update({f"{param}": f"{val}"})
            if self.parameters:
                sql_param.update(self.parameters)
            if isinstance(self.sql, str):
                final_sql.append(SQL(self.sql))
            else:
                final_sql.extend(list(map(SQL, self.sql)))
            results = self.hook.run(
                final_sql,
                self.autocommit,
                parameters=sql_param,
                handler=self.handler,
            )
        else:
            results = self.hook.run(
                self.sql,
                self.autocommit,
                parameters=self.parameters,
                handler=self.handler,
            )
        for output in self.hook.conn.notices:
            self.log.info(output)

        return results
