"""
# Create New Index DAG

TODO: Docstring
"""
import logging
import os

from airflow import DAG
from airflow.models.param import Param
from es.create_new_es_index import create_new_es_index as es
from es.create_new_es_index.create_new_es_index_types import (
    CREATE_NEW_INDEX_CONFIGS,
    CreateNewIndex,
)

from common.constants import AUDIO, DAG_DEFAULT_ARGS, MEDIA_TYPES


logger = logging.getLogger(__name__)


def create_new_es_index_dag(config: CreateNewIndex):
    dag = DAG(
        dag_id=config.dag_id,
        default_args=DAG_DEFAULT_ARGS,
        schedule=None,
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        tags=["elasticsearch"],
        render_template_as_native_obj=True,
        params={
            "media_type": Param(
                default=AUDIO,
                enum=MEDIA_TYPES,
                description="The media type for which to create the index.",
            ),
            "index_config": Param(
                default={},
                type=["object"],
                description=(
                    "A JSON object containing the configuration for the new index."
                    " The values in this object will be merged with the existing"
                    " configuration, where the value specified at a leaf key in the"
                    " object will override the existing value (see Merging policy in"
                    " the DAG docs). This can also be the entire index configuration,"
                    " in which case the existing configuration will be replaced entirely"
                    " (see override_config parameter below)."
                ),
            ),
            "index_suffix": Param(
                default=None,
                type=["string", "null"],
                description=(
                    "The name suffix of the new index to create. This will be a string,"
                    " and will be used to name the index in Elasticsearch of the form"
                    " {media_type}-{index_suffix}. If not provided, the suffix will be a"
                    " timestamp of the form YYYYMMDDHHMMSS."
                ),
            ),
            "source_index": Param(
                default=None,
                type=["string", "null"],
                description=(
                    "The existing index on Elasticsearch to use as the basis for the new"
                    " index. If not provided, the index aliased to media_type will be used"
                    " (e.g. image for the image media type)."
                ),
            ),
            "query": Param(
                default={},
                type=["object"],
                description=(
                    "An optional Elasticsearch query to use to filter the documents to be"
                    " copied to the new index. If not provided, all documents will be"
                    " copied."
                ),
            ),
            "override_config": Param(
                default=False,
                type="boolean",
                description=(
                    " A boolean value which can be toggled to replace the existing index"
                    " configuration entirely with the new configuration. If True, the"
                    " index_config parameter will be used as the entire configuration. If"
                    " False, the index_config parameter will be merged with the existing"
                    " configuration."
                ),
            ),
        },
    )

    # TODO: separate variables were necessary because we can't just get the value of
    # Airflow connection vars, they get interpreted as Connection objects
    es_host = os.getenv(f"ELASTICSEARCH_HTTP_{config.environment.upper()}")

    with dag:
        prevent_concurrency = es.prevent_concurrency_with_dags(config.blocking_dags)

        index_name = es.get_index_name(
            media_type="{{ params.media_type }}",
            index_suffix="{{ params.index_suffix or ts_nodash }}",
        )

        check_override = es.check_override_config(
            override="{{ params.override_config }}"
        )

        current_index_config = es.get_current_index_configuration(
            source_index="{{ params.source_index or params.media_type }}",
            es_host=es_host,
        )

        merged_index_config = es.merge_index_configurations(
            new_index_config="{{ params.index_config }}",
            current_index_config=current_index_config,
        )

        final_index_config = es.get_final_index_configuration(
            override_config="{{ params.override_config }}",
            index_config="{{ params.index_config }}",
            # May resolve to None if tasks were skipped
            merged_config=merged_index_config,
            index_name=index_name,
        )

        create_new_index = es.create_index(
            index_config=final_index_config, es_host=es_host
        )

        reindex = es.trigger_and_wait_for_reindex(
            index_name=index_name,
            source_index="{{ params.source_index or params.media_type }}",
            query="{{ params.query }}",
            es_host=es_host,
        )

        # Set up dependencies
        prevent_concurrency >> index_name
        index_name >> check_override >> [current_index_config, final_index_config]
        current_index_config >> merged_index_config >> final_index_config
        final_index_config >> create_new_index >> reindex

    return dag


for config in CREATE_NEW_INDEX_CONFIGS:
    # Generate the DAG for this environment
    globals()[config.dag_id] = create_new_es_index_dag(config)
