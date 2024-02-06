"""
Monitor staging and production Elasticsearch cluster health endpoint.

Requests the cluster health and alerts under the following conditions:

- Red cluster health
- Unexpected number of nodes
- Unresponsive cluster

Additionally, the DAG will notify (rather than alert) when the cluster health is yellow.
Yellow cluster health may or may not be an issue, depending on whether it is expected,
and occurs whenever shards and replicas are being relocated (e.g., during reindexes).
It is worthwhile to notify in these cases, as an assurance, but we could choose to add
logic that ignores yellow cluster health during data refresh or other similar operations.
"""

import json
import logging
from datetime import datetime

from airflow.decorators import dag, task
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from elasticsearch import Elasticsearch

from common.constants import PRODUCTION, STAGING, Environment
from common.slack import send_alert, send_message
from elasticsearch_cluster.shared import get_es_host


logger = logging.getLogger(__name__)


_DAG_ID = "{env}_elasticsearch_cluster_healthcheck"

EXPECTED_NODE_COUNT = 6
EXPECTED_DATA_NODE_COUNT = 3
EXPECTED_MASTER_NODE_COUNT = 3


def _format_response_body(response_body: dict) -> str:
    return f"""
    Full healthcheck response body:
    ```
    {json.dumps(response_body, indent=4)}
    ```
    """


def _compose_red_status(env: Environment, response_body: dict):
    message = f"""
    Elasticsearch {env} cluster status is **red**.

    This is a critical status change, **investigate ASAP**.

    {_format_response_body(response_body)}
    """
    return message


def _compose_unexpected_node_count(env: Environment, response_body: dict):
    node_count = response_body["number_of_nodes"]
    data_node_count = response_body["number_of_data_nodes"]
    master_node_count = node_count - data_node_count

    message = f"""
    Elasticsearch {env} cluster node count is **{node_count}**.
    Expected {EXPECTED_NODE_COUNT} total nodes.

    Master nodes: **{master_node_count}** of expected {EXPECTED_MASTER_NODE_COUNT}
    Data nodes: **{data_node_count}** of expected {EXPECTED_DATA_NODE_COUNT}

    This is a critical status change, **investigate ASAP**.
    If this is expected (e.g., during controlled node or cluster changes), acknowledge immediately with explanation.

    {_format_response_body(response_body)}
    """
    logger.error(f"Unexpected node count; {json.dumps(response_body)}")
    return message


def _compose_yellow_cluster_health(env: Environment, response_body: dict):
    message = f"""
    Elasticsearch {env} cluster health is **yellow**.

    This does not mean something is necessarily wrong, but if this is not expected (e.g., data refresh) then investigate cluster health now.

    {_format_response_body(response_body)}
    """
    logger.info(f"Cluster health was yellow; {json.dumps(response_body)}")
    return message


@task
def ping_healthcheck(env: str, es_host: str):
    es_conn: Elasticsearch = ElasticsearchPythonHook(hosts=[es_host]).get_conn

    response = es_conn.cluster.health()

    return response.body


@task
def compose_notification(env: Environment, response_body: dict):
    status = response_body["status"]

    if status == "red":
        return "alert", _compose_red_status(env, response_body)

    if response_body["number_of_nodes"] != EXPECTED_NODE_COUNT:
        return "alert", _compose_unexpected_node_count(env, response_body)

    if status == "yellow":
        return "notification", _compose_yellow_cluster_health(env, response_body)

    logger.info(f"Cluster health was green; {json.dumps(response_body)}")
    return None, None


@task
def notify(env: str, message_type_and_string: tuple[str, str]):
    message_type, message = message_type_and_string

    if message_type == "alert":
        send_alert(message, dag_id=_DAG_ID.format(env=env))
    elif message_type == "notification":
        send_message(message, dag_id=_DAG_ID.format(env=env))


def _cluster_healthcheck_dag(env: Environment):
    es_host = get_es_host(env)
    healthcheck_response = ping_healthcheck(env, es_host)
    notification = compose_notification(env, healthcheck_response)
    es_host >> healthcheck_response >> notification >> notify(env, notification)


_SHARED_DAG_ARGS = {
    # Every 15 minutes
    "schedule": "*/15 * * * *",
    "start_date": datetime(2024, 2, 4),
    "catchup": False,
    "max_active_runs": 1,
    "doc_md": __doc__,
    "tags": ["elasticsearch", "monitoring"],
}


@dag(dag_id=_DAG_ID.format(env=STAGING), **_SHARED_DAG_ARGS)
def staging_elasticsearch_cluster_healthcheck():
    _cluster_healthcheck_dag(STAGING)


@dag(dag_id=_DAG_ID.format(env=PRODUCTION), **_SHARED_DAG_ARGS)
def production_elasticsearch_cluster_healthcheck():
    _cluster_healthcheck_dag(PRODUCTION)


staging_elasticsearch_cluster_healthcheck()
production_elasticsearch_cluster_healthcheck()
