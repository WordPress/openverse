import pytest
from airflow.exceptions import AirflowSkipException

from common.constants import PRODUCTION
from elasticsearch_cluster.healthcheck_dag import compose_notification


_TEST_ENV = "testing_environment"


def _make_response_body(**kwargs):
    # Default values based on real response from Openverse staging cluster
    # Only the `cluster_name` is changed to reflect the environment
    return {
        "cluster_name": "testcluster",
        "status": "green",
        "timed_out": False,
        "number_of_nodes": 6,
        "number_of_data_nodes": 3,
        "active_primary_shards": 51,
        "active_shards": 103,
        "relocating_shards": 0,
        "initializing_shards": 0,
        "unassigned_shards": 0,
        "delayed_unassigned_shards": 0,
        "number_of_pending_tasks": 0,
        "number_of_in_flight_fetch": 0,
        "task_max_waiting_in_queue_millis": 0,
        "active_shards_percent_as_number": 100,
    } | kwargs


def _missing_node_keys(master_nodes: int, data_nodes: int):
    total_nodes = master_nodes + data_nodes
    return (
        f"Elasticsearch {_TEST_ENV} cluster node count is **{total_nodes}**",
        "Expected 6 total nodes.",
        f"Master nodes: **{master_nodes}** of expected 3",
        f"Data nodes: **{data_nodes}** of expected 3",
    )


@pytest.mark.parametrize(
    ("expected_message_type", "message_keys", "cluster_health_response"),
    (
        pytest.param(
            "alert",
            (f"Elasticsearch {_TEST_ENV} cluster status is **red**",),
            _make_response_body(status="red"),
            id="red-status",
        ),
        pytest.param(
            "alert",
            _missing_node_keys(master_nodes=3, data_nodes=2),
            _make_response_body(
                status="yellow",
                number_of_nodes=5,
                number_of_data_nodes=2,
            ),
            id="missing-data-node",
        ),
        pytest.param(
            "alert",
            _missing_node_keys(master_nodes=2, data_nodes=3),
            _make_response_body(
                status="yellow",
                number_of_nodes=5,
                number_of_data_nodes=3,
            ),
            id="missing-master-node",
        ),
        pytest.param(
            "alert",
            _missing_node_keys(master_nodes=1, data_nodes=2),
            _make_response_body(
                status="yellow",
                number_of_nodes=3,
                number_of_data_nodes=2,
            ),
            id="missing-some-of-both-node-types",
        ),
        pytest.param(
            "notification",
            (f"Elasticsearch {_TEST_ENV} cluster health is **yellow**.",),
            _make_response_body(
                status="yellow",
            ),
            id="yellow-status-all-nodes-present",
        ),
        pytest.param(
            None,
            None,
            _make_response_body(status="green"),
            id="green-status",
            marks=pytest.mark.raises(exception=AirflowSkipException),
        ),
    ),
)
def test_compose_notification(
    expected_message_type, message_keys, cluster_health_response
):
    message_type, message = compose_notification.function(
        _TEST_ENV, cluster_health_response, is_data_refresh_running=False
    )

    assert message_type == expected_message_type
    for message_key in message_keys:
        assert message_key in message


def test_production_compose_notification_data_refresh_running():
    with pytest.raises(AirflowSkipException):
        cluster_health_response = _make_response_body(status="yellow")
        compose_notification.function(
            PRODUCTION,
            cluster_health_response,
            is_data_refresh_running=True,
        )


def test_production_compose_notification_data_refresh_not_running():
    cluster_health_response = _make_response_body(status="yellow")
    message_type, message = compose_notification.function(
        PRODUCTION,
        cluster_health_response,
        is_data_refresh_running=False,
    )

    assert message_type == "notification"
    assert "Elasticsearch production cluster health is **yellow**." in message
