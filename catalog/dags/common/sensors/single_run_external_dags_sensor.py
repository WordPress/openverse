from collections.abc import Iterable

from airflow.sensors.base import BaseSensorOperator

from common.dag_state import count_running_dag_runs_past_task


class SingleRunExternalDAGsSensor(BaseSensorOperator):
    """
    Sensor for ensuring only one DAG runs at a time.

    Waits for a list of related DAGs, each assumed to have a similar Sensor,
    to not be running. A related DAG is considered to be 'running' if it is
    itself in the running state, and its corresponding wait task completed
    successfully. It looks for a task with the same `task_id` in each of the
    provided external DAGs.

    The DAG parsing tests check that each external DAG exists and has a task with
    this sensor's `task_id`.

    :param external_dag_ids: A list of dag_ids that you want to wait for
    :param allow_concurrent_runs: Used to force the Sensor to pass, even
    if there are concurrent runs.
    """

    def __init__(
        self,
        *,
        external_dag_ids: Iterable[str],
        allow_concurrent_runs: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.external_dag_ids = external_dag_ids
        self.allow_concurrent_runs = allow_concurrent_runs

    def poke(self, context):
        self.log.info(
            "Poking for DAGs %s ...",
            self.external_dag_ids,
        )

        if self.allow_concurrent_runs:
            self.log.info(
                "`allow_concurrent_runs` is enabled. Returning without"
                " checking for running DAGs."
            )
            return True

        count_running = self.get_count()

        self.log.info("%s DAGs are in the running state", count_running)
        return count_running == 0

    def get_count(self) -> int:
        # Get the count of running DAGs. A DAG is considered 'running' if
        # the DAG itself is in the running state, and if its instance of
        # the Sensor task has completed successfully.
        return sum(
            count_running_dag_runs_past_task(dag_id, self.task_id)
            for dag_id in self.external_dag_ids
        )
