"""
# Create Proportional By Source Staging Index DAG

This DAG is used to create a new staging Elasticsearch index that is a subset
of a production source index, such that the proportions of records by source in
the new index is equal to the proportions of records by source in the source
index.


Required Dagrun Configuration parameters:

* media_type:         The media type for which to create a new index.
* percentage_of_prod: A float indicating the proportion of items to take from each
                      source from the total amount existing in the production
                      source index

Optional params:

* source_index: An existing production Elasticsearch index to use as the basis for
                the new index. If not provided, the index aliased to
                `<media_type>-filtered` will be used.

## When this DAG runs

This DAG is on a `None` schedule and is run manually.

## Race conditions

Because this DAG runs on the staging ingestion server and staging elasticsearch
cluster, it does _not_ interfere with the `data_refresh` or
`create_filtered_index` DAGs.

However, as the DAG operates on the staging API database it will exit
immediately if any of the following DAGs are running:
* `staging_database_restore`
* `recreate_full_staging_index`
* `create_new_staging_es_index`
"""
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.models import Variable
from airflow.models.param import Param

from common import elasticsearch as es
from common import slack
from common.constants import (
    AUDIO,
    DAG_DEFAULT_ARGS,
    MEDIA_TYPES,
    STAGING,
)
from common.sensors.utils import prevent_concurrency_with_dags
from database.staging_database_restore.constants import (
    DAG_ID as STAGING_DB_RESTORE_DAG_ID,
)
from elasticsearch_cluster.create_new_es_index.create_new_es_index_types import (
    CREATE_NEW_INDEX_CONFIGS,
)
from elasticsearch_cluster.create_proportional_by_source_staging_index import (
    create_proportional_by_source_staging_index as create_index,
)
from elasticsearch_cluster.recreate_staging_index.recreate_full_staging_index import (
    DAG_ID as RECREATE_STAGING_INDEX_DAG_ID,
)


DAG_ID = "create_proportional_by_source_staging_index"


@dag(
    dag_id=DAG_ID,
    default_args=DAG_DEFAULT_ARGS,
    schedule=None,
    start_date=datetime(2024, 1, 31),
    tags=["database", "elasticsearch"],
    max_active_runs=1,
    catchup=False,
    doc_md=__doc__,
    params={
        "media_type": Param(
            default=AUDIO,
            enum=MEDIA_TYPES,
            description="The media type for which to create the index.",
        ),
        "percentage_of_prod": Param(
            default=0.5,
            type="number",
            minimum=0,
            maximum=1,
            description=(
                "The proportion of items to take of each provider from"
                " the total amount existing in the source index."
            ),
        ),
        "source_index": Param(
            default=None,
            type=["string", "null"],
            description=(
                "Optionally, the existing production Elasticsearch index"
                " to use as the basis for the new index. If not provided,"
                " the index aliased to `<media_type>-filtered` will be used."
            ),
        ),
    },
    render_template_as_native_obj=True,
)
def create_proportional_by_source_staging_index():
    # Fail early if any conflicting DAGs are running
    prevent_concurrency = prevent_concurrency_with_dags(
        external_dag_ids=[
            STAGING_DB_RESTORE_DAG_ID,
            RECREATE_STAGING_INDEX_DAG_ID,
            CREATE_NEW_INDEX_CONFIGS[STAGING].dag_id,
        ]
    )

    es_host = es.get_es_host(environment=STAGING)

    source_index_name = create_index.get_source_index(
        source_index="{{ params.source_index }}",
        media_type="{{ params.media_type }}",
    )

    source_config = es.get_index_configuration(
        source_index=source_index_name, es_host=es_host
    )

    destination_index_name = create_index.get_destination_index_name(
        media_type="{{ params.media_type }}",
        current_datetime_str="{{ ts_nodash }}",
        percentage_of_prod="{{ params.percentage_of_prod }}",
    )

    destination_alias = create_index.get_destination_alias(
        media_type="{{ params.media_type }}"
    )

    destination_index_config = create_index.get_destination_index_config(
        source_config=source_config, destination_index_name=destination_index_name
    )

    new_index = es.create_index(index_config=destination_index_config, es_host=es_host)

    production_source_counts = create_index.get_production_source_counts(
        source_index=source_index_name, es_host=es_host
    )

    desired_source_counts = create_index.get_proportional_source_count_kwargs.override(
        task_id="get_desired_source_counts"
    )(
        production_source_counts=production_source_counts,
        percentage_of_prod="{{ params.percentage_of_prod }}",
    )

    reindex = es.trigger_and_wait_for_reindex.partial(
        destination_index=destination_index_name,
        source_index=source_index_name,
        timeout=timedelta(hours=12),
        requests_per_second=Variable.get(
            "ES_INDEX_THROTTLING_RATE", 20_000, deserialize_json=True
        ),
        # When slices are used to parallelize indexing, max_docs does
        # not work reliably and the final proportions may be incorrect.
        slices=None,
        es_host=es_host,
    ).expand_kwargs(desired_source_counts)

    point_alias = es.point_alias(
        index_name=destination_index_name, alias=destination_alias, es_host=es_host
    )

    notify_completion = slack.notify_slack(
        text=f"Reindexing complete for {destination_index_name}.",
        dag_id=DAG_ID,
        username="Proportional by Source Staging Index Creation",
        icon_emoji=":elasticsearch:",
    )

    # Setup additional dependencies
    prevent_concurrency >> es_host
    es_host >> [source_index_name, destination_index_name, destination_alias]
    production_source_counts >> desired_source_counts
    new_index >> production_source_counts
    reindex >> point_alias >> notify_completion


create_proportional_by_source_staging_index()
