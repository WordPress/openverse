import logging

import pytest
from airflow.exceptions import AirflowException
from airflow.models import DagBag, Pool
from airflow.models.dag import DAG
from airflow.utils.state import State
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType

from common.sensors.single_run_external_dags_sensor import SingleRunExternalDAGsSensor


DEFAULT_DATE = datetime(2022, 1, 1)
TEST_TASK_ID = "wait_task"
DEV_NULL = "/dev/null"


def run_sensor(sensor):
    sensor.run(start_date=DEFAULT_DATE, end_date=DEFAULT_DATE, ignore_ti_state=True)


def create_task(dag, task_id, sample_pool_fixture):
    return SingleRunExternalDAGsSensor(
        task_id=task_id,
        external_dag_ids=[],
        check_existence=True,
        dag=dag,
        pool=sample_pool_fixture,
        poke_interval=5,
        mode="reschedule",
    )


def create_dag(
    dag_id, sample_dag_id_fixture, sample_pool_fixture, task_id=TEST_TASK_ID
):
    with DAG(
        f"{sample_dag_id_fixture}_{dag_id}",
        default_args={
            "owner": "airflow",
            "start_date": DEFAULT_DATE,
        },
    ) as dag:
        # Create a sensor task inside the DAG
        create_task(dag, task_id, sample_pool_fixture)

    return dag


def create_dagrun(dag, dag_state):
    return dag.create_dagrun(
        run_id=f"{dag.dag_id}_test",
        start_date=DEFAULT_DATE,
        execution_date=DEFAULT_DATE,
        data_interval=(DEFAULT_DATE, DEFAULT_DATE),
        state=dag_state,
        run_type=DagRunType.MANUAL,
    )


@pytest.fixture
def setup_pool(sample_pool_fixture):
    Pool.create_or_update_pool(
        sample_pool_fixture,
        slots=1,
        description="test pool",
        include_deferred=False,
    )


@pytest.mark.usefixtures("clean_db")
# This appears to be coming from Airflow internals during testing as a result of
# loading the example DAGs:
# /opt/airflow/.local/lib/python3.10/site-packages/airflow/example_dags/example_subdag_operator.py:43: RemovedInAirflow3Warning  # noqa: E501
@pytest.mark.filterwarnings(
    "ignore:This class is deprecated. Please use "
    "`airflow.utils.task_group.TaskGroup`.:airflow.exceptions.RemovedInAirflow3Warning"
)
# This also appears to be coming from Airflow internals during testing as a result of
# loading the example bash operator DAG:
# /home/airflow/.local/lib/python3.10/site-packages/airflow/models/dag.py:3492: RemovedInAirflow3Warning  # noqa: E501
@pytest.mark.filterwarnings(
    "ignore:Param `schedule_interval` is deprecated and will be removed in a future release. "
    "Please use `schedule` instead.:airflow.exceptions.RemovedInAirflow3Warning"
)
def test_fails_if_external_dag_does_not_exist(clean_db, setup_pool):
    with pytest.raises(
        AirflowException,
        match="The external DAG nonexistent_dag_id does not exist.",
    ):
        dag = DAG(
            "test_missing_dag_error",
            default_args={
                "owner": "airflow",
                "start_date": DEFAULT_DATE,
            },
        )
        sensor = SingleRunExternalDAGsSensor(
            task_id=TEST_TASK_ID,
            external_dag_ids=[
                "nonexistent_dag_id",
            ],
            check_existence=True,
            poke_interval=5,
            mode="reschedule",
            dag=dag,
        )

        run_sensor(sensor)


@pytest.mark.filterwarnings(
    "ignore:This class is deprecated. Please use "
    "`airflow.utils.task_group.TaskGroup`.:airflow.exceptions.RemovedInAirflow3Warning"
)
# This also appears to be coming from Airflow internals during testing as a result of
# loading the example bash operator DAG:
# /home/airflow/.local/lib/python3.10/site-packages/airflow/models/dag.py:3492: RemovedInAirflow3Warning  # noqa: E501
@pytest.mark.filterwarnings(
    "ignore:Param `schedule_interval` is deprecated and will be removed in a future release. "
    "Please use `schedule` instead.:airflow.exceptions.RemovedInAirflow3Warning"
)
def test_fails_if_external_dag_missing_sensor_task(clean_db, setup_pool):
    # Loads an example DAG which does not have a Sensor task.
    dagbag = DagBag(dag_folder=DEV_NULL, include_examples=True)
    bash_dag = dagbag.dags["example_bash_operator"]
    bash_dag.sync_to_db()

    error_msg = (
        "The external DAG example_bash_operator does not have a task"
        f" with id {TEST_TASK_ID}"
    )
    with pytest.raises(AirflowException, match=error_msg):
        dag = DAG(
            "test_missing_task_error",
            default_args={
                "owner": "airflow",
                "start_date": DEFAULT_DATE,
            },
        )
        sensor = SingleRunExternalDAGsSensor(
            task_id=TEST_TASK_ID,
            external_dag_ids=[
                "example_bash_operator",
            ],
            check_existence=True,
            poke_interval=5,
            mode="reschedule",
            dag=dag,
        )

        run_sensor(sensor)


@pytest.mark.filterwarnings(
    "ignore:This class is deprecated. Please use "
    "`airflow.utils.task_group.TaskGroup`.:airflow.exceptions.RemovedInAirflow3Warning"
)
# This also appears to be coming from Airflow internals during testing as a result of
# loading the example bash operator DAG:
# /home/airflow/.local/lib/python3.10/site-packages/airflow/models/dag.py:3492: RemovedInAirflow3Warning  # noqa: E501
@pytest.mark.filterwarnings(
    "ignore:Param `schedule_interval` is deprecated and will be removed in a future release. "
    "Please use `schedule` instead.:airflow.exceptions.RemovedInAirflow3Warning"
)
def test_succeeds_if_no_running_dags(
    caplog, sample_dag_id_fixture, sample_pool_fixture, clean_db, setup_pool
):
    # Create some DAGs that are not considered 'running'
    successful_dag = create_dag(
        "successful_dag", sample_dag_id_fixture, sample_pool_fixture
    )
    create_dagrun(successful_dag, State.SUCCESS)
    failed_dag = create_dag("failed_dag", sample_dag_id_fixture, sample_pool_fixture)
    create_dagrun(failed_dag, State.FAILED)

    # DAG in the running state, but its wait task has not been started
    queued_dag = create_dag("queued_dag", sample_dag_id_fixture, sample_pool_fixture)
    create_dagrun(queued_dag, State.RUNNING)

    # Create the Test DAG and sensor with dependent dag Ids
    dag = DAG(
        "test_dag_success",
        default_args={
            "owner": "airflow",
            "start_date": DEFAULT_DATE,
        },
    )
    sensor = SingleRunExternalDAGsSensor(
        task_id=TEST_TASK_ID,
        external_dag_ids=["successful_dag", "failed_dag", "queued_dag"],
        poke_interval=5,
        mode="reschedule",
        dag=dag,
        pool=sample_pool_fixture,
    )
    with caplog.at_level(logging.INFO):
        run_sensor(sensor)
        assert (
            "Poking for DAGs ['successful_dag', 'failed_dag', 'queued_dag'] ..."
            in caplog.text
        )
        assert "0 DAGs are in the running state" in caplog.text


@pytest.mark.filterwarnings(
    "ignore:This class is deprecated. Please use "
    "`airflow.utils.task_group.TaskGroup`.:airflow.exceptions.RemovedInAirflow3Warning"
)
# This also appears to be coming from Airflow internals during testing as a result of
# loading the example bash operator DAG:
# /home/airflow/.local/lib/python3.10/site-packages/airflow/models/dag.py:3492: RemovedInAirflow3Warning  # noqa: E501
@pytest.mark.filterwarnings(
    "ignore:Param `schedule_interval` is deprecated and will be removed in a future release. "
    "Please use `schedule` instead.:airflow.exceptions.RemovedInAirflow3Warning"
)
def test_retries_if_running_dags_with_completed_sensor_task(
    caplog, sample_dag_id_fixture, sample_pool_fixture, clean_db, setup_pool
):
    # Create a DAG in the 'running' state
    running_dag = create_dag("running_dag", sample_dag_id_fixture, sample_pool_fixture)
    running_dagrun = create_dagrun(running_dag, State.RUNNING)

    pool = Pool.get_pool(sample_pool_fixture)
    assert pool.open_slots() == 1

    # Run its sensor task and ensure that it succeeds
    ti = running_dagrun.get_task_instance(task_id=TEST_TASK_ID)
    ti.task = running_dag.get_task(task_id=TEST_TASK_ID)
    ti.run()
    assert ti.state == State.SUCCESS

    # Create a DAG that is not in the running state
    successful_dependent_dag = create_dag(
        "success_dag", sample_dag_id_fixture, sample_pool_fixture
    )
    create_dagrun(successful_dependent_dag, State.SUCCESS)

    # Create the Test DAG and sensor and set up dependent dag Ids
    dag = DAG(
        "test_dag_failure",
        default_args={
            "owner": "airflow",
            "start_date": DEFAULT_DATE,
        },
    )
    sensor = SingleRunExternalDAGsSensor(
        task_id=TEST_TASK_ID,
        external_dag_ids=[
            f"{sample_dag_id_fixture}_success_dag",
            f"{sample_dag_id_fixture}_running_dag",
        ],
        poke_interval=5,
        mode="reschedule",
        dag=dag,
        pool=sample_pool_fixture,
    )

    with caplog.at_level(logging.INFO):
        run_sensor(sensor)

        assert (
            f"Poking for DAGs ['"
            f"{sample_dag_id_fixture}_success_dag', '{sample_dag_id_fixture}_running_dag'] ..."
            in caplog.text
        )
        assert "1 DAGs are in the running state" in caplog.text
