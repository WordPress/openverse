"""
# Create New ES Index DAG

This file generates our Create New ES Index DAGs using a factory function. A
separate DAG is generated for the staging and production environments.

Each DAG can be used to create new Elasticsearch indices in their respective
environment, based on an existing index. The following configuration options
are available:

* `media_type`     : media type for which to create the new index
* `index_suffix`   : optional suffix to be added to the new index name. If not
                     supplied, a creation timestamp is used.
* `source_index`   : the existing index on which to base the new index, and from
                     which to copy records
* `index_config`   : a JSON object containing the configuration for the new index.
                     By default, this will be merged into the configuration of the
                     source index according to the merging policy documented below.
* `query`          : an optional Elasticsearch query, used to filter the documents
                     copied from the source index into the new index. If not
                     supplied, all records are copied.
* `override_config`: boolean override; when True, the `index_config` will be used
                     for the new index configuration _without_ merging any values
                     from the source index config.
* `target_alias`   : optional alias to be applied to the new index after reindexing.
                     If the alias already applies to an existing index, it will be
                     removed first.
* `should_delete_old_index`: whether to remove the index previously pointed to by
                     the target_alias, if it exists. Defaults to False.

## Merging policy

The configuration will be merged such that a leaf key in the `index_config` overwrites
the entire value present in the source configuration at that key. The leaf values are
merged naively, so a list for instance is replaced entirely (rather than appending
values). For example, if the base configuration is:

```
{
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "type": "stemmer_override",
                    "rules": [
                        "animals => animal",
                        "animal => animal",
                        "anime => anime",
                        "animate => animate",
                        "animated => animate",
                        "universe => universe"
                    ]
                }
            }
        }
    }
}
```

And the `index_config` passed in is:

```
{
    "settings": {
        "index": {
            "number_of_shards": 2,
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "rules": ["crim => cribble"]
                }
            }
        }
    }
}
```

The resulting, merged configuration will be:

```
{
    "settings": {
        "index": {
            "number_of_shards": 2,
            "number_of_replicas": 1
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "type": "stemmer_override",
                    "rules": ["crim => cribble"]
                }
            }
        }
    }
}
```

## Race conditions

Each DAG will fail immediately if any of the DAGs tagged as part of the
es-concurrency group for the DAG's environment is running. (E.g., the
`create_new_staging_es_index` DAG fails immediately if any DAGs tagged with
`staging-es-concurrency` are running.)
"""

import logging

from airflow import DAG
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

from common import elasticsearch as es
from common import slack
from common.constants import AUDIO, DAG_DEFAULT_ARGS, MEDIA_TYPES
from common.sensors.utils import prevent_concurrency_with_dags_with_tag
from elasticsearch_cluster.create_new_es_index.create_new_es_index import (
    GET_CURRENT_INDEX_CONFIG_TASK_NAME,
    GET_FINAL_INDEX_CONFIG_TASK_NAME,
    check_override_config,
    get_final_index_configuration,
    get_index_name,
    merge_index_configurations,
)
from elasticsearch_cluster.create_new_es_index.create_new_es_index_types import (
    CREATE_NEW_INDEX_CONFIGS,
    CreateNewIndex,
)


logger = logging.getLogger(__name__)


def create_new_es_index_dag(config: CreateNewIndex):
    dag = DAG(
        dag_id=config.dag_id,
        default_args=DAG_DEFAULT_ARGS,
        schedule=None,
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        tags=["elasticsearch", config.concurrency_tag],
        render_template_as_native_obj=True,
        params={
            "media_type": Param(
                default=AUDIO,
                enum=MEDIA_TYPES,
                description="The media type for which to create the index.",
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
            "query": Param(
                default={},
                type=["object", "null"],
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
            "target_alias": Param(
                default=None,
                type=["string", "null"],
                description=(
                    "Optional alias which will be applied to the newly created index. If"
                    " the alias already exists, it will first be removed from the"
                    " index to which it previously pointed."
                ),
            ),
            "should_delete_old_index": Param(
                default=False,
                type="boolean",
                description=(
                    "Whether to delete the index previously pointed to by the"
                    " `target_alias`."
                ),
            ),
        },
    )

    with dag:
        # Fail early if any other DAG that operates on the relevant elasticsearch cluster
        # is running
        prevent_concurrency = prevent_concurrency_with_dags_with_tag(
            tag=config.concurrency_tag, excluded_dag_ids=[config.dag_id]
        )

        es_host = es.get_es_host(environment=config.environment)

        index_name = get_index_name(
            media_type="{{ params.media_type }}",
            index_suffix="{{ params.index_suffix or ts_nodash }}",
        )

        check_override = check_override_config(override="{{ params.override_config }}")

        current_index_config = es.get_index_configuration.override(
            task_id=GET_CURRENT_INDEX_CONFIG_TASK_NAME
        )(
            source_index="{{ params.source_index or params.media_type }}",
            es_host=es_host,
        )

        merged_index_config = merge_index_configurations(
            new_index_config="{{ params.index_config }}",
            current_index_config=current_index_config,
        )

        final_index_config = get_final_index_configuration.override(
            task_id=GET_FINAL_INDEX_CONFIG_TASK_NAME,
            trigger_rule=TriggerRule.NONE_FAILED,
        )(
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
            destination_index=index_name,
            source_index="{{ params.source_index or params.media_type }}",
            query="{{ params.query }}",
            timeout=config.reindex_timeout,
            requests_per_second=config.requests_per_second,
            es_host=es_host,
        )

        point_alias = es.point_alias(
            es_host=es_host,
            target_index=index_name,
            target_alias="{{ params.target_alias }}",
            should_delete_old_index="{{ params.should_delete_old_index }}",
        )

        notify_completion = slack.notify_slack.override(
            trigger_rule=TriggerRule.NONE_FAILED
        )(
            text=(
                f"New index { index_name } was successfully created with alias"
                "{{ params.target_alias }}."
            ),
            dag_id=dag.dag_id,
            username="Create New ES Index",
            icon_emoji=":elasticsearch:",
        )

        # Set up dependencies
        prevent_concurrency >> [es_host, index_name]
        index_name >> check_override >> [current_index_config, final_index_config]
        current_index_config >> merged_index_config >> final_index_config
        final_index_config >> create_new_index >> reindex >> point_alias
        point_alias >> notify_completion

    return dag


for config in CREATE_NEW_INDEX_CONFIGS.values():
    # Generate the DAG for this environment
    globals()[config.dag_id] = create_new_es_index_dag(config)
