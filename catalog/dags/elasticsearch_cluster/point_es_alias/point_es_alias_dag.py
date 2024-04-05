"""
# Point ES Alias DAG

This file generates our Point ES Alias DAGs using a factory function. A
separate DAG is generated for the staging and production environments.

The DAGs are used to point a `target_alias` to a `target_index` in the
given environment's elasticsearch cluster. When the alias is applied, it
is first removed from any existing index to which it already applies;
optionally, it can also delete that index afterward.

## When this DAG runs

This DAG is on a `None` schedule and is run manually.

## Race conditions

Each DAG will fail immediately if any of the DAGs tagged as part of the
es-concurrency group for the DAG's environment is running. (E.g., the
`point_staging_alias` DAG fails immediately if any DAGs tagged with
`staging-es-concurrency` are running.)
"""

from datetime import datetime

from airflow import DAG
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

from common import elasticsearch as es
from common import slack
from common.constants import (
    DAG_DEFAULT_ARGS,
    ENVIRONMENTS,
)
from common.sensors.constants import ES_CONCURRENCY_TAGS
from common.sensors.utils import prevent_concurrency_with_dags_with_tag


def point_es_alias_dag(environment: str):
    dag = DAG(
        dag_id=f"point_{environment}_es_alias",
        default_args=DAG_DEFAULT_ARGS,
        schedule=None,
        start_date=datetime(2024, 1, 31),
        tags=["elasticsearch", ES_CONCURRENCY_TAGS[environment]],
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        params={
            "target_index": Param(
                type="string",
                description=(
                    "The existing Elasticsearch index to which the target alias"
                    " should be applied."
                ),
            ),
            "target_alias": Param(
                type="string",
                description=(
                    "The alias which will be applied to the index. If"
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
        render_template_as_native_obj=True,
    )

    with dag:
        # Fail early if any other DAG that operates on the elasticsearch cluster for
        # this environment is running
        prevent_concurrency = prevent_concurrency_with_dags_with_tag(
            tag=ES_CONCURRENCY_TAGS[environment],
        )

        es_host = es.get_es_host(environment=environment)

        point_alias = es.point_alias(
            es_host=es_host,
            target_index="{{ params.target_index }}",
            target_alias="{{ params.target_alias }}",
            should_delete_old_index="{{ params.should_delete_old_index }}",
        )

        notify_completion = slack.notify_slack.override(
            trigger_rule=TriggerRule.NONE_FAILED
        )(
            text="Alias {{ params.target_alias }} applied to index {{ params.target_index }}.",
            dag_id=dag.dag_id,
            username="Point Alias",
            icon_emoji=":elasticsearch:",
        )

        prevent_concurrency >> es_host >> point_alias >> notify_completion


for environment in ENVIRONMENTS:
    point_es_alias_dag(environment)
