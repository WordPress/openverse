import pytest
from airflow.utils.session import create_session
from airflow.models import DagRun, Pool, TaskInstance


def pytest_addoption(parser):
    """
    Add options to pytest.

    This functions alters the pytest CLI command options. It adds an "extended" flag
    which will run tests that take a significant amount of time that may not be useful
    for rapid local iteration.

    Adapted from:
    https://stackoverflow.com/a/43938191/3277713 CC BY-SA 4.0
    """
    parser.addoption(
        "--extended",
        action="store_true",
        dest="extended",
        default=False,
        help="Run time-consuming 'extended' tests",
    )


# Use this decorator on tests which are expected to take a long time and would best be
# run on CI only
mark_extended = pytest.mark.skipif("not config.getoption('extended')")

@pytest.fixture()
def get_test_dag_id():
    return ""

@pytest.fixture()
def get_test_pool():
    return ""
@pytest.fixture()
def isTaskInstance():
    return False

@pytest.fixture()
def isPool():
    return False

@pytest.fixture(autouse=True)
def clean_db(get_test_dag_id, get_test_pool, isTaskInstance, isPool):
    with create_session() as session:
        # synchronize_session='fetch' required here to refresh models
        # https://stackoverflow.com/a/51222378 CC BY-SA 4.0
        session.query(DagRun).filter(DagRun.dag_id == get_test_dag_id).delete()
        if isTaskInstance:
            session.query(TaskInstance).filter(
                TaskInstance.dag_id == get_test_dag_id
            ).delete(synchronize_session="fetch")
        if isPool:
            session.query(Pool).filter(id == get_test_pool).delete()