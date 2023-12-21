import pytest
from airflow.models import DagRun, Pool, TaskInstance
from airflow.utils.session import create_session


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


def _normalize_test_module_name(request) -> str:
    # Extract the test name
    name = request.module.__name__
    # Replace periods with two underscores
    return name.replace(".", "__")


@pytest.fixture
def sample_dag_id_fixture(request):
    return f"{_normalize_test_module_name(request)}_dag"


@pytest.fixture
def sample_pool_fixture(request):
    return f"{_normalize_test_module_name(request)}_pool"


@pytest.fixture
def clean_db(sample_dag_id_fixture, sample_pool_fixture):
    with create_session() as session:
        # synchronize_session='fetch' required here to refresh models
        # https://stackoverflow.com/a/51222378 CC BY-SA 4.0
        session.query(DagRun).filter(
            DagRun.dag_id.startswith(sample_dag_id_fixture)
        ).delete(synchronize_session="fetch")
        session.query(TaskInstance).filter(
            TaskInstance.dag_id.startswith(sample_dag_id_fixture)
        ).delete(synchronize_session="fetch")
        session.query(Pool).filter(Pool.pool.startswith(sample_pool_fixture)).delete(
            synchronize_session="fetch"
        )


@pytest.fixture
def setup_pool(sample_pool_fixture):
    Pool.create_or_update_pool(
        sample_pool_fixture,
        slots=1,
        description="test pool",
        include_deferred=False,
    )
