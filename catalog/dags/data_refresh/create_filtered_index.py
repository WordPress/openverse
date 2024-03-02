"""
# Create filtered index TaskGroup factory

This module contains factory functions used to generate the Airflow tasks for
creating filtered indices, used by the data refreshes of each media type and the
Create Filtered Index DAGs.

Filtered index creation is handled by the ingestion server. The TaskGroups generated
by the ``create_filtered_index_creation_task_groups`` function in this module are
responsible for creating and promoting filtered indices. The ``create_filtered_index``
TaskGroup trigges the ingestion server action to create and populate the filtered
index for a given media type, and awaits the completion of the index creation. The
``promote_filtered_index`` TaskGroup awaits healthy results from the newly created
index, and then points the filtered index alias for the media type to the new index,
finally deleting the old, now unused filtered index. These TaskGroups are used in
the data refresh DAGs to execute the filtered index steps.
"""

from datetime import timedelta

from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from common import ingestion_server
from common.constants import XCOM_PULL_TEMPLATE
from data_refresh.data_refresh_types import DataRefresh


def create_and_populate_filtered_index(
    media_type: str,
    data_refresh: DataRefresh,
    origin_index_suffix: str | None,
    destination_index_suffix: str | None,
):
    create_payload = {}
    if origin_index_suffix:
        create_payload["origin_index_suffix"] = origin_index_suffix
    if destination_index_suffix:
        create_payload["destination_index_suffix"] = destination_index_suffix

    return ingestion_server.trigger_and_wait_for_task(
        action="CREATE_AND_POPULATE_FILTERED_INDEX",
        model=media_type,
        data=create_payload or None,
        timeout=data_refresh.create_filtered_index_timeout,
    )


def point_alias(
    media_type: str, target_alias: str, destination_index_suffix: str
) -> TaskGroup:
    point_alias_payload = {
        "alias": target_alias,
        "index_suffix": f"{destination_index_suffix}-filtered",
    }

    with TaskGroup(group_id="point_alias") as point_alias_group:
        ingestion_server.trigger_and_wait_for_task(
            action="POINT_ALIAS",
            model=media_type,
            data=point_alias_payload,
            timeout=timedelta(hours=12),  # matches the ingestion server's wait time
        )
    return point_alias_group


def create_filtered_index_creation_task_groups(
    data_refresh: DataRefresh,
    origin_index_suffix: str | None,
    destination_index_suffix: str | None,
) -> tuple[TaskGroup, TaskGroup]:
    """
    Create the TaskGroups that performs filtered index creation and promotion for
    the given DataRefresh.
    """
    media_type = data_refresh.media_type
    target_alias = f"{media_type}-filtered"

    with TaskGroup(group_id="create_filtered_index") as create_filtered_index_group:
        # If a destination index suffix isn't provided, we need to generate
        # one so that we know where to point the alias
        final_destination_index_suffix = (
            ingestion_server.generate_index_suffix.override(
                task_id="generate_filtered_index_suffix"
            )(destination_index_suffix)
        )

        # Determine the current index. The current index retrieval has to happen prior
        # to any of the index creation steps to ensure the appropriate index information
        # is retrieved.
        get_current_index_if_exists = ingestion_server.get_current_index(target_alias)

        # The current index retrieval step can be skipped if the index does not
        # currently exist. The empty operator below works as a control flow management
        # step to ensure the create step runs even if the current index retrieval step
        # is skipped (the trigger rule would be tedious to percolate through all the
        # helper functions to the index creation step itself).
        continue_if_no_current_index = EmptyOperator(
            task_id="continue_if_no_current_index",
            trigger_rule=TriggerRule.NONE_FAILED,
        )

        do_create, await_create = create_and_populate_filtered_index(
            media_type=media_type,
            data_refresh=data_refresh,
            origin_index_suffix=origin_index_suffix,
            destination_index_suffix=final_destination_index_suffix,
        )

        get_current_index_if_exists >> continue_if_no_current_index >> do_create
        do_create >> await_create

    with TaskGroup(group_id="promote_filtered_index") as promote_filtered_index_group:
        # Await healthy results from the newly created elasticsearch index, then trigger
        # and await the promotion of the index.
        index_readiness_check = ingestion_server.index_readiness_check(
            media_type=media_type,
            index_suffix=f"{final_destination_index_suffix}-filtered",
        )

        do_point_alias = point_alias(
            media_type=media_type,
            target_alias=target_alias,
            destination_index_suffix=final_destination_index_suffix,
        )

        delete_old_index = ingestion_server.trigger_task(
            action="DELETE_INDEX",
            model=data_refresh.media_type,
            data={
                "index_suffix": XCOM_PULL_TEMPLATE.format(
                    get_current_index_if_exists.task_id, "return_value"
                ),
            },
        )

        index_readiness_check >> do_point_alias

        [get_current_index_if_exists, do_point_alias] >> delete_old_index

    return create_filtered_index_group, promote_filtered_index_group
