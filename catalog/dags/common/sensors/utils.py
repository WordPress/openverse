from datetime import datetime

from airflow.models import DagRun


def get_most_recent_dag_run(dag_id) -> list[datetime] | datetime:
    """
    Retrieve the most recent DAG run's execution date.

    For use as ``execution_date_fn`` argument to ``ExternalTaskSensor``.

    Adapted from https://stackoverflow.com/a/74017474
    CC BY-SA 4.0 by Stack Overflow user Nahid O.
    """
    dag_runs = DagRun.find(dag_id=dag_id)
    dag_runs.sort(key=lambda x: x.execution_date, reverse=True)
    if dag_runs:
        return dag_runs[0].execution_date

    # If there are no DAG runs, return an empty list to indicate that
    # there are no execution dates to check.
    # This works because the sensor waits until the number
    # of runs for the execution dates in the ``allowed_states`` matches the
    # length of the list of execution dates to check. If there are no runs
    # for this DAG, then the only possible number of required states
    # we can have is 0. See ``ExternalTaskSensor::poke`` and
    # ``ExternalTaskSensor::get_count``, especially the handling
    # of ``dttm_filter`` for the relevant implementation details.
    return []
