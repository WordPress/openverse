from pathlib import Path

import pytest
from airflow.models import DagBag

from common.constants import MEDIA_TYPES
from providers.provider_reingestion_workflows import (
    PROVIDER_REINGESTION_WORKFLOWS as REINGESTION_WORKFLOW_CONFIGS,
)
from providers.provider_workflows import PROVIDER_WORKFLOWS as PROVIDER_WORKFLOW_CONFIGS


# The path to DAGs *within the container*, though that should mirror the current
# directory structure.
DAG_FOLDER = Path(__file__).parents[2] / "dags"

# DAG paths to test
DAG_PATHS = [
    "providers/provider_workflow_dag_factory.py",
    "maintenance/airflow_log_cleanup_workflow.py",
    "maintenance/pr_review_reminders/pr_review_reminders_dag.py",
    "maintenance/rotate_db_snapshots.py",
    "popularity/recreate_popularity_calculation_dag_factory.py",
    "popularity/popularity_refresh_dag_factory.py",
    "data_refresh/dag_factory.py",
    "data_refresh/create_filtered_index_dag.py",
    "elasticsearch/recreate_staging_index/recreate_full_staging_index_dag.py",
    "oauth2/authorize_dag.py",
    "oauth2/token_refresh_dag.py",
    "database/delete_records/delete_records_dag.py",
]

# Expected count from the DagBag once a file has been parsed
# (this will likely not need to be edited for new providers)
EXPECTED_COUNT = {
    "providers/provider_workflow_dag_factory.py": len(PROVIDER_WORKFLOW_CONFIGS),
    "providers/provider_ingestion_workflow_dag_factory.py": len(
        REINGESTION_WORKFLOW_CONFIGS
    ),
    "popularity/recreate_popularity_calculation_dag_factory.py": len(MEDIA_TYPES),
    "popularity/popularity_refresh_dag_factory.py": len(MEDIA_TYPES),
    "data_refresh/dag_factory.py": len(MEDIA_TYPES),
    "data_refresh/create_filtered_index_dag.py": len(MEDIA_TYPES),
}


def test_dag_import_errors():
    # Attempt to load all DAGs in the DAG_FOLDER, and detect import
    # errors
    dagbag = DagBag(dag_folder=DAG_FOLDER, include_examples=False)

    dag_errors = []
    for filename in dagbag.import_errors.keys():
        dag_errors.append(Path(filename).name)
    error_string = ",".join(dag_errors)

    assert (
        len(dagbag.import_errors) == 0
    ), f"Errors found during DAG import for files: {error_string}"


# relative_path represents the path from the DAG folder to the file
@pytest.mark.parametrize("relative_path", DAG_PATHS)
def test_dags_loads_correct_number_with_no_errors(relative_path, tmpdir):
    # For each configured DAG file, test that the expected number of DAGs
    # is loaded. Assume only 1 DAG is expected unless otherwise provided
    expected_count = EXPECTED_COUNT.get(relative_path, 1)
    dag_bag = DagBag(dag_folder=tmpdir, include_examples=False)
    dag_bag.process_file(str(DAG_FOLDER / relative_path))
    assert len(dag_bag.import_errors) == 0, "Errors found during DAG import"
    assert len(dag_bag.dags) == expected_count, "An unexpected # of DAGs was found"
