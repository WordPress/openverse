"""
# Recreate Full Staging Index DAG

This DAG is used to fully recreate a new staging Elasticsearch index for a
given `media_type`, using records pulled from the staging API database rather than
from a source index (like the `create_new_staging_es_index` DAG does). It is
used to decouple the steps of creating a new index from the rest of the
data refresh process.

Staging index creation is handled by the _staging_ ingestion server. The DAG
triggers the ingestion server `REINDEX` action to create a new index in the
staging elasticsearch cluster for the given media type, suffixed by the current
timestamp. The DAG awaits the completion of the index creation and then points
the `<media_type>-full` alias to the newly created index.

Required Dagrun Configuration parameters:

* media_type: the media type for which to create a new index.

Optional params:

* target_alias_override: Override the alias that is pointed to the new index. By
                         default this is `<media_type>-full`.
* delete_old_index:      Whether to delete the index previously pointed to by the
                         target alias, if applicable. Defaults to False.

## When this DAG runs

This DAG is on a `None` schedule and is run manually.

## Race conditions

Because this DAG runs on the staging ingestion server and staging elasticsearch
cluster, it does _not_ interfere with the `data_refresh` or
`create_filtered_index` DAGs.

However, as the DAG operates on the staging API database and ES cluster it will exit
immediately if any of the DAGs tagged as part of the `staging_es_concurrency` group
are already running.
"""

from datetime import datetime

from airflow.decorators import dag
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

from common import ingestion_server, slack
from common.constants import (
    AUDIO,
    DAG_DEFAULT_ARGS,
    MEDIA_TYPES,
    XCOM_PULL_TEMPLATE,
)
from common.sensors.constants import (
    STAGING_DB_CONCURRENCY_TAG,
    STAGING_ES_CONCURRENCY_TAG,
)
from common.sensors.utils import prevent_concurrency_with_dags_with_tag
from elasticsearch_cluster.recreate_staging_index.recreate_full_staging_index import (
    DAG_ID,
    create_index,
    get_target_alias,
    point_alias,
    should_delete_index,
)


@dag(
    dag_id=DAG_ID,
    default_args=DAG_DEFAULT_ARGS,
    schedule=None,
    start_date=datetime(2023, 4, 1),
    tags=[
        "database",
        "elasticsearch",
        STAGING_DB_CONCURRENCY_TAG,
        STAGING_ES_CONCURRENCY_TAG,
    ],
    max_active_runs=1,
    catchup=False,
    doc_md=__doc__,
    params={
        "media_type": Param(
            default=AUDIO,
            enum=MEDIA_TYPES,
            description="The media type for which to create the index.",
        ),
        "target_alias_override": Param(
            default=None,
            type=["string", "null"],
            description=(
                "Optionally, override the target alias for the newly created index."
                " The default to `{media_type}-full` using the given media_type."
            ),
        ),
        "delete_old_index": Param(
            default=False,
            type="boolean",
            description=(
                "Whether to delete the index previously pointed to be the "
                "`target_alias`, if it is replaced. The index will "
                "only be deleted if the alias was successfully linked to the "
                " newly created index."
            ),
        ),
    },
    render_template_as_native_obj=True,
)
def recreate_full_staging_index():
    # Fail early if any other DAG that operates on the staging elasticsearch cluster
    # is running
    prevent_concurrency_es = prevent_concurrency_with_dags_with_tag.override(
        group_id="prevent_concurrency_with_elasticsearch_dags"
    )(
        tag=STAGING_ES_CONCURRENCY_TAG,
    )

    # Because this DAG pulls records from the staging API database during reindexing
    # rather than reindexing from another ES index, it must also prevent concurrency
    # with DAGs that affect the staging DB.
    prevent_concurrency_db = prevent_concurrency_with_dags_with_tag.override(
        group_id="prevent_concurrency_with_api_db_dags"
    )(
        tag=STAGING_DB_CONCURRENCY_TAG,
    )

    target_alias = get_target_alias(
        media_type="{{ params.media_type }}",
        target_alias_override="{{ params.target_alias_override }}",
    )

    # Suffix the index with a current timestamp.
    new_index_suffix = ingestion_server.generate_index_suffix.override(
        trigger_rule=TriggerRule.NONE_FAILED
    )("full-{{ ts_nodash.lower() }}")

    # Get the index currently aliased by the target_alias, in case it must be
    # deleted later.
    get_current_index_if_exists = ingestion_server.get_current_index(
        target_alias, http_conn_id="staging_data_refresh"
    )

    # Create the new Elasticsearch index
    do_create_index = create_index(
        media_type="{{ params.media_type }}", index_suffix=new_index_suffix
    )

    # Actually point the alias
    do_point_alias = point_alias(
        media_type="{{ params.media_type }}",
        target_alias=target_alias,
        index_suffix=new_index_suffix,
    )

    check_if_should_delete_index = should_delete_index(
        should_delete="{{ params.delete_old_index }}",
        old_index=XCOM_PULL_TEMPLATE.format(
            get_current_index_if_exists.task_id, "return_value"
        ),
    )

    # Branch only reached if check_if_should_delete_index is True.
    # Deletes the old index pointed to by the target_alias after the alias has been
    # unlinked.
    delete_old_index = ingestion_server.trigger_task(
        action="DELETE_INDEX",
        model="{{ params.media_type }}",
        data={
            "index_suffix": XCOM_PULL_TEMPLATE.format(
                get_current_index_if_exists.task_id, "return_value"
            ),
        },
        http_conn_id="staging_data_refresh",
    )

    notify_complete = slack.notify_slack.override(
        task_id="notify_complete", trigger_rule=TriggerRule.NONE_FAILED
    )(
        text=(
            "Finished creating full staging index `{{ params.media_type }}-"
            f"{new_index_suffix}` aliased to `{target_alias}`."
        ),
        username="Full Staging Index Creation",
        dag_id=DAG_ID,
    )

    # Set up dependencies
    prevent_concurrency_es >> target_alias
    prevent_concurrency_db >> target_alias

    target_alias >> get_current_index_if_exists >> new_index_suffix
    new_index_suffix >> do_create_index >> do_point_alias
    do_point_alias >> check_if_should_delete_index
    check_if_should_delete_index >> [delete_old_index, notify_complete]
    delete_old_index >> notify_complete


recreate_full_staging_index()
