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
from textwrap import dedent, indent
from typing import Literal

from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook
from elasticsearch import Elasticsearch

from common.constants import DAG_DEFAULT_ARGS, ENVIRONMENTS, PRODUCTION, Environment
from common.elasticsearch import get_es_host
from common.sensors.utils import is_concurrent_with_any
from common.slack import send_alert, send_message
from legacy_data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS


logger = logging.getLogger(__name__)


_DAG_ID = "{env}_elasticsearch_cluster_healthcheck"

EXPECTED_NODE_COUNT = 6
EXPECTED_DATA_NODE_COUNT = 3
EXPECTED_MASTER_NODE_COUNT = 3
MessageType = Literal["alert", "notification"]


def _format_response_body(response_body: dict) -> str:
    body_str = indent(json.dumps(response_body, indent=4), prefix=" " * 4)
    # body_str is indented in, because the f string added an indentation to
    # the front, causing the first curly brace to be incorrectly indented
    # and interpolating a multi-line string into the f string led subsequent lines
    # to have incorrect indentation (they did not incorporate the f-strings
    # own indentation.
    # Adding our own indentation using `indent` to match the f-strings
    # allows us to correctly dedent later on without issue, with a uniform indentation
    # on every line.
    return f"""
    Full healthcheck response body:
    ```
{body_str}
    ```
    """


def _compose_red_status(env: Environment, response_body: dict) -> str:
    message = f"""
    Elasticsearch {env} cluster status is **red**.

    This is a critical status change, **investigate ASAP**.

    {_format_response_body(response_body)}
    """
    return message


def _compose_unexpected_node_count(env: Environment, response_body: dict) -> str:
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


def _compose_yellow_cluster_health(env: Environment, response_body: dict) -> str:
    message = f"""
    Elasticsearch {env} cluster health is **yellow**.

    This does not mean something is necessarily wrong, but if this is not expected (e.g., data refresh) then investigate cluster health now.

    {_format_response_body(response_body)}
    """
    logger.info(f"Cluster health was yellow; {json.dumps(response_body)}")
    return message


@task
def ping_healthcheck(env: str, es_host: str) -> dict:
    es_conn: Elasticsearch = ElasticsearchPythonHook(hosts=[es_host]).get_conn

    response = es_conn.cluster.health()

    return response.body


@task
def compose_notification(
    env: Environment, response_body: dict, is_data_refresh_running: bool
) -> tuple[MessageType, str]:
    status = response_body["status"]

    if status == "red":
        return "alert", _compose_red_status(env, response_body)

    if response_body["number_of_nodes"] != EXPECTED_NODE_COUNT:
        return "alert", _compose_unexpected_node_count(env, response_body)

    if status == "yellow":
        if is_data_refresh_running and env == PRODUCTION:
            raise AirflowSkipException(
                "Production cluster health status is yellow during data refresh. "
                "This is an expected state, so no alert is sent."
            )

        return "notification", _compose_yellow_cluster_health(env, response_body)

    raise AirflowSkipException(f"Cluster health is green; {json.dumps(response_body)}")


@task
def notify(env: str, message_type_and_string: tuple[MessageType, str]):
    message_type, message = message_type_and_string

    if message_type == "alert":
        send_alert(dedent(message), dag_id=_DAG_ID.format(env=env))
    elif message_type == "notification":
        send_message(dedent(message), dag_id=_DAG_ID.format(env=env))
    else:
        raise ValueError(
            f"Invalid message_type. Expected 'alert' or 'notification', "
            f"received {message_type}"
        )


_SHARED_DAG_ARGS = {
    # Every 15 minutes
    "schedule": "*/15 * * * *",
    "start_date": datetime(2024, 2, 4),
    "catchup": False,
    "max_active_runs": 1,
    "doc_md": __doc__,
    "tags": ["elasticsearch", "monitoring"],
    "default_args": DAG_DEFAULT_ARGS,
}


_DATA_REFRESH_DAG_IDS = []
for config in DATA_REFRESH_CONFIGS.values():
    _DATA_REFRESH_DAG_IDS += [config.dag_id, config.filtered_index_dag_id]


for env in ENVIRONMENTS:

    @dag(dag_id=_DAG_ID.format(env=env), **_SHARED_DAG_ARGS)
    def cluster_healthcheck_dag():
        is_data_refresh_running = is_concurrent_with_any(_DATA_REFRESH_DAG_IDS)

        es_host = get_es_host(env)
        healthcheck_response = ping_healthcheck(env, es_host)
        notification = compose_notification(
            env, healthcheck_response, is_data_refresh_running
        )
        es_host >> healthcheck_response >> notification >> notify(env, notification)

    cluster_healthcheck_dag()
