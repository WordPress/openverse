from pathlib import Path

import pytest
from airflow.models import DagBag

from common.constants import ENVIRONMENTS, MEDIA_TYPES
from common.sensors.constants import CONCURRENCY_TAG_DAG_IDS
from common.sensors.single_run_external_dags_sensor import SingleRunExternalDAGsSensor
from providers.provider_reingestion_workflows import (
    PROVIDER_REINGESTION_WORKFLOWS as REINGESTION_WORKFLOW_CONFIGS,
)
from providers.provider_workflows import PROVIDER_WORKFLOWS as PROVIDER_WORKFLOW_CONFIGS


# The path to DAGs *within the container*, though that should mirror the current
# directory structure.
DAG_FOLDER = Path(__file__).parents[2] / "dags"

# DAG paths to test
DAG_PATHS = [
    "data_refresh/dag_factory.py",
    "database/batched_update/batched_update_dag.py",
    "database/catalog_cleaner/catalog_cleaner.py",
    "data_augmentation/rekognition/add_rekognition_labels_dag.py",
    "database/delete_records/delete_records_dag.py",
    "database/report_pending_reported_media.py",
    "database/staging_database_restore/staging_database_restore_dag.py",
    "elasticsearch_cluster/create_new_es_index/create_new_es_index_dag.py",
    "elasticsearch_cluster/create_proportional_by_source_staging_index/create_proportional_by_source_staging_index_dag.py",  # noqa: E501
    "elasticsearch_cluster/healthcheck_dag.py",
    "elasticsearch_cluster/point_es_alias/point_es_alias_dag.py",
    "elasticsearch_cluster/recreate_staging_index/recreate_full_staging_index_dag.py",
    "legacy_data_refresh/create_filtered_index_dag.py",
    "legacy_data_refresh/dag_factory.py",
    "maintenance/add_license_url.py",
    "maintenance/airflow_log_cleanup_workflow.py",
    "maintenance/check_silenced_dags.py",
    "maintenance/decode_and_deduplicate_image_tags.py",
    "maintenance/flickr_audit_sub_provider_workflow.py",
    "maintenance/pr_review_reminders/pr_review_reminders_dag.py",
    "maintenance/rotate_db_snapshots.py",
    "maintenance/rotate_envfiles.py",
    "oauth2/authorize_dag.py",
    "oauth2/token_refresh_dag.py",
    "popularity/popularity_refresh_dag_factory.py",
    "popularity/recreate_popularity_calculation_dag_factory.py",
    "providers/provider_reingestion_workflow_dag_factory.py",
    "providers/provider_workflow_dag_factory.py",
]

# Expected count from the DagBag once a file has been parsed
# (this will likely not need to be edited for new providers)
EXPECTED_COUNT = {
    "providers/provider_workflow_dag_factory.py": len(PROVIDER_WORKFLOW_CONFIGS),
    "providers/provider_reingestion_workflow_dag_factory.py": len(
        REINGESTION_WORKFLOW_CONFIGS
    ),
    "popularity/recreate_popularity_calculation_dag_factory.py": len(MEDIA_TYPES),
    "popularity/popularity_refresh_dag_factory.py": len(MEDIA_TYPES),
    "legacy_data_refresh/dag_factory.py": len(MEDIA_TYPES),
    "legacy_data_refresh/create_filtered_index_dag.py": len(MEDIA_TYPES),
    "elasticsearch_cluster/healthcheck_dag.py": len(ENVIRONMENTS),
    "data_refresh/dag_factory.py": len(MEDIA_TYPES) * len(ENVIRONMENTS),
    "database/batched_update/batched_update_dag.py": 2,
    "elasticsearch_cluster/create_new_es_index/create_new_es_index_dag.py": len(
        ENVIRONMENTS
    ),
    "elasticsearch_cluster/point_es_alias/point_es_alias_dag.py": len(ENVIRONMENTS),
}


def test_dag_import_errors():
    # Attempt to load all DAGs in the DAG_FOLDER, and detect import
    # errors
    dagbag = DagBag(dag_folder=DAG_FOLDER)

    dag_errors = []
    for filename in dagbag.import_errors.keys():
        dag_errors.append(Path(filename).name)
    error_string = ",".join(dag_errors)

    assert len(dagbag.import_errors) == 0, (
        f"Errors found during DAG import for files: {error_string}"
    )

    all_paths = {
        str(Path(dag.fileloc).relative_to(DAG_FOLDER)) for dag in dagbag.dags.values()
    }
    missing_paths = all_paths - set(DAG_PATHS)
    assert len(missing_paths) == 0, (
        f"The following DAG files are unaccounted for in the DAG parse testing, "
        f"please add them to `DAG_PATHS` in `test_dag_parsing.py`: {missing_paths}"
    )


# relative_path represents the path from the DAG folder to the file
@pytest.mark.parametrize("relative_path", DAG_PATHS)
def test_dags_loads_correct_number_with_no_errors(relative_path, tmpdir):
    # For each configured DAG file, test that the expected number of DAGs
    # is loaded. Assume only 1 DAG is expected unless otherwise provided
    expected_count = EXPECTED_COUNT.get(relative_path, 1)
    dag_bag = DagBag(dag_folder=tmpdir)
    dag_bag.process_file(str(DAG_FOLDER / relative_path))
    assert len(dag_bag.dags), "No DAGs found in file"
    assert len(dag_bag.import_errors) == 0, "Errors found during DAG import"
    found = len(dag_bag.dags)
    assert found == expected_count, f"An unexpected # of DAGs ({found}) were found"


def test_dag_uses_default_args():
    # Attempt to load all DAGs in the DAG_FOLDER and check if they use the
    # DAG_DEFAULT_ARGS settings
    dagbag = DagBag(dag_folder=DAG_FOLDER)

    failures = []
    for dag_id, dag in dagbag.dags.items():
        # An easy proxy for this is checking if DAGs have an on_failure_callback
        on_failure_callback = dag.default_args.get("on_failure_callback")
        if on_failure_callback is None:
            failures.append(dag_id)

    assert not failures, (
        f"The following DAGs do not have DAG_DEFAULT_ARGS defined: {failures}"
    )


@pytest.fixture(scope="module")
def all_dags():
    return DagBag(dag_folder=DAG_FOLDER).dags


def test_concurrency_tag_dag_ids_match_dag_tags(all_dags):
    # Concurrency checks read `CONCURRENCY_TAG_DAG_IDS` instead of the DAG tags, so
    # the two must stay in sync
    for tag, dag_ids in CONCURRENCY_TAG_DAG_IDS.items():
        tagged = sorted(dag_id for dag_id, dag in all_dags.items() if tag in dag.tags)
        assert sorted(dag_ids) == tagged, (
            f"Update `CONCURRENCY_TAG_DAG_IDS[{tag!r}]` to match the DAGs with the tag"
        )

    all_tags = {tag for dag in all_dags.values() for tag in dag.tags}
    unlisted = {tag for tag in all_tags if tag.endswith("_concurrency")} - set(
        CONCURRENCY_TAG_DAG_IDS
    )
    assert not unlisted, f"Add these tags to `CONCURRENCY_TAG_DAG_IDS`: {unlisted}"


def test_single_run_sensors_wait_on_existing_tasks(all_dags):
    # The sensor looks for a task with its own task id in each external DAG
    sensors = [
        (dag_id, task)
        for dag_id, dag in all_dags.items()
        for task in dag.tasks
        if isinstance(task, SingleRunExternalDAGsSensor)
    ]
    assert sensors

    for dag_id, sensor in sensors:
        for external_dag_id in sensor.external_dag_ids:
            assert external_dag_id in all_dags, (
                f"{dag_id}.{sensor.task_id} waits on a missing DAG {external_dag_id}"
            )
            assert all_dags[external_dag_id].has_task(sensor.task_id), (
                f"{external_dag_id} has no {sensor.task_id} task for {dag_id} to wait on"
            )


def test_concurrency_tagged_dags_have_one_active_run(all_dags):
    # The concurrency sensors wait while any run of a tagged DAG is active, which
    # matches waiting on its latest run only while each DAG runs one at a time
    tagged_dag_ids = {
        dag_id for dag_ids in CONCURRENCY_TAG_DAG_IDS.values() for dag_id in dag_ids
    }
    for dag_id in tagged_dag_ids:
        assert all_dags[dag_id].max_active_runs == 1, dag_id
