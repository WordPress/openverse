from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import State

from common.constants import REFRESH_POKE_INTERVAL
from common.sensors.utils import get_most_recent_dag_run


class ExternalDAGSensor(ExternalTaskSensor):
    """
    Sensor for awaiting the completion of an external DAG.

    This is a very simple extension of the ExternalTaskSensor which
    supplies defaults commonly used for awaiting the completion of an
    entire DAG, rather than a particular task.

    :param external_dag_id: The id of the DAG to wait for
    """

    def __init__(
        self,
        *,
        external_dag_id: str,
        **kwargs,
    ):
        super().__init__(
            # Defaults which can be overridden
            poke_interval=REFRESH_POKE_INTERVAL,
            **kwargs,
            # Defaults applied after kwargs can not be
            # overridden by kwargs
            external_dag_id=external_dag_id,
            # Wait for the whole DAG, not just a part of it
            external_task_id=None,
            check_existence=False,
            execution_date_fn=lambda _: get_most_recent_dag_run(external_dag_id),
            mode="reschedule",
            # Any "finished" state is sufficient for us to continue
            allowed_states=[State.SUCCESS, State.FAILED],
        )
