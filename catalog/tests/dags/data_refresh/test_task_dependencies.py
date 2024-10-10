"""
Tests vital dependencies for the data refresh: for example, ensuring that the indices have been
created and refreshed before index promotion runs. These dependencies can be broken in
unexpected ways so it is important to verify that the most critical ones are preserved.
"""

import logging

from airflow.models import DagBag


logger = logging.getLogger(__name__)


def test_staging_schedule():
    dagbag = DagBag()

    # Assert that all of the staging data refresh DAGs
    # have a schedule of None
    for dag in [
        dag for dag in dagbag.dags.values() if "staging_data_refresh" in dag.tags
    ]:
        assert dag.schedule_interval is None, (
            "Staging data refresh DAGs must be on a `None` schedule"
            " or risk breaking the load_sample_data script."
        )


def _assert_dependencies(downstream_task_id: str, upstream_task_ids: list[str]):
    dag = DagBag().get_dag("staging_image_data_refresh")

    downstream_task = dag.get_task(downstream_task_id)
    # Get all upstream tasks for this task, not just the direct upstream tasks
    upstream_tasks = downstream_task.get_flat_relative_ids(upstream=True)

    for upstream_task_id in upstream_task_ids:
        assert upstream_task_id in upstream_tasks


def test_dependencies_alter_data_task():
    _assert_dependencies(
        downstream_task_id="alter_table_data.alter_data_batch",
        upstream_task_ids=["copy_upstream_tables.copy_upstream_table.copy_data"],
    )


def test_dependencies_reindex_task():
    _assert_dependencies(
        downstream_task_id="run_distributed_reindex.reindex.trigger_reindexing_task",
        upstream_task_ids=[
            "copy_upstream_tables.copy_upstream_table.copy_data",
            "alter_table_data.alter_data_batch",
            "create_index",
        ],
    )


def test_dependencies_create_and_populate_filtered_index_task():
    _assert_dependencies(
        downstream_task_id="create_and_populate_filtered_index.trigger_and_wait_for_reindex.trigger_reindex",
        upstream_task_ids=[
            "run_distributed_reindex.reindex.assert_reindexing_success",
            "run_distributed_reindex.refresh_index",
        ],
    )


def test_dependencies_promote_table_task():
    _assert_dependencies(
        downstream_task_id="promote_tables.promote_table.promote",
        upstream_task_ids=[
            "run_distributed_reindex.reindex.assert_reindexing_success",
            "create_and_populate_filtered_index.refresh_index",
            "promote_tables.promote_table.remap_table_indices_to_table.create_table_indices",
            "promote_tables.promote_table.remap_table_constraints_to_table.apply_constraints_to_table",
        ],
    )


def test_dependenceis_promote_index_task():
    _assert_dependencies(
        downstream_task_id="promote_index.point_new_alias",
        upstream_task_ids=[
            "run_distributed_reindex.refresh_index",
            "promote_tables.promote_table.promote",
        ],
    )


def test_dependenceis_promote_filtered_index_task():
    _assert_dependencies(
        downstream_task_id="promote_filtered_index.point_new_alias",
        upstream_task_ids=[
            "create_and_populate_filtered_index.refresh_index",
            "promote_tables.promote_table.promote",
        ],
    )
