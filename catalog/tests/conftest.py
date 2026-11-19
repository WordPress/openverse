import fcntl
import json
import tempfile
from pathlib import Path

# Registers the FAB `ab_user` table that `task_instance_note` references; without it,
# deleting task instances fails to resolve the foreign key.
import airflow.providers.fab.auth_manager.models  # noqa: F401
import pytest
from airflow.utils.json import XComDecoder, XComEncoder


def xcom_round_trip(value):
    """
    Return `value` as a downstream task receives it, after Airflow stores it as a JSON
    XCom. Tuples, including NamedTuples, come back as lists.
    """
    return json.loads(json.dumps(value, cls=XComEncoder), cls=XComDecoder)


def run_dag_test(dag):
    """
    Run `dag.test()` on a DAG defined in a test.

    `dag.test()` only serializes DAGs it finds by parsing the DAG bundle, so a DAG
    built inside a test has to be written to the metadata database first.

    `dag.test()` also writes every DAG in the bundle to the database, so two xdist
    workers running it at once collide on the `dag` table's primary key. A file lock
    runs one at a time.
    """
    from airflow.dag_processing.dagbag import DagBag, sync_bag_to_db

    with open(Path(tempfile.gettempdir()) / "catalog-dag-test.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        dagbag = DagBag(collect_dags=False, bundle_name="dags-folder")
        dagbag.bag_dag(dag)
        sync_bag_to_db(dagbag, "dags-folder", None)
        return dag.test()


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
