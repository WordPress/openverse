from pathlib import Path

import pytest
from airflow.models import DagBag
from common.constants import MEDIA_TYPES
from providers.provider_ingestion_workflows import (
    PROVIDER_INGESTION_WORKFLOWS as INGESTION_WORKFLOW_CONFIGS,
)
from providers.provider_workflows import PROVIDER_WORKFLOWS as PROVIDER_WORKFLOW_CONFIGS


# The path to DAGs *within the container*, though that should mirror the current
# directory structure.
DAG_FOLDER = Path(__file__).parents[2] / "openverse_catalog" / "dags"

# DAG paths to test
DAG_PATHS = [
    "providers/provider_workflow_dag_factory.py",
    "maintenance/airflow_log_cleanup_workflow.py",
    "commoncrawl/sync_commoncrawl_workflow.py",
    "commoncrawl/commoncrawl_etl.py",
    "database/loader_workflow.py",
    "database/recreate_popularity_calculation_dag_factory.py",
    "data_refresh/dag_factory.py",
    "oauth2/authorize_dag.py",
    "oauth2/token_refresh_dag.py",
]

# Expected count from the DagBag once a file has been parsed
# (this will likely not need to be edited for new providers)
EXPECTED_COUNT = {
    "providers/provider_workflow_dag_factory.py": len(PROVIDER_WORKFLOW_CONFIGS),
    "providers/provider_ingestion_workflow_dag_factory.py": len(
        INGESTION_WORKFLOW_CONFIGS
    ),
    "database/recreate_popularity_calculation_dag_factory.py": len(MEDIA_TYPES),
    "data_refresh/dag_factory.py": len(MEDIA_TYPES),
}


# relative_path represents the path from the DAG folder to the file
@pytest.mark.parametrize("relative_path", DAG_PATHS)
def test_dag_loads_with_no_errors(relative_path, tmpdir):
    # Assume only 1 DAG is expected unless otherwise provided
    expected_count = EXPECTED_COUNT.get(relative_path, 1)
    dag_bag = DagBag(dag_folder=tmpdir, include_examples=False)
    dag_bag.process_file(str(DAG_FOLDER / relative_path))
    assert len(dag_bag.import_errors) == 0, "Errors found during DAG import"
    assert len(dag_bag.dags) == expected_count, "An unexpected # of DAGs was found"
