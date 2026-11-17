import logging
from unittest import mock

import pytest
import requests
from airflow.providers.amazon.aws.hooks.ec2 import EC2Hook

from common.constants import PRODUCTION
from data_refresh.constants import INDEXER_WORKER_REQUEST_TIMEOUT
from data_refresh.distributed_reindex import (
    get_worker_url,
    trigger_reindexing_task,
    wait_for_reindexing_task,
    wait_for_worker,
)


logger = logging.getLogger(__name__)


def _build_instance_status_response(
    instance_state,
    instance_status,
    system_status,
    attached_ebs_status,
    instance_reachability_status,
    system_reachability_status,
    attached_ebs_reachability_status,
):
    return {
        "InstanceStatuses": [
            {
                "AvailabilityZone": "us-east-1a",
                "InstanceId": "i-01234abc",
                "InstanceState": {"Code": 16, "Name": instance_state},
                "InstanceStatus": {
                    "Details": [
                        {"Name": "reachability", "Status": instance_reachability_status}
                    ],
                    "Status": instance_status,
                },
                "SystemStatus": {
                    "Details": [
                        {"Name": "reachability", "Status": system_reachability_status}
                    ],
                    "Status": system_status,
                },
                "AttachedEbsStatus": {
                    "Details": [
                        {
                            "Name": "reachability",
                            "Status": attached_ebs_reachability_status,
                        }
                    ],
                    "Status": attached_ebs_status,
                },
            }
        ],
        "ResponseMetadata": {
            "RequestId": "123abc-def-456-789",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "x-amzn-requestid": "123abc-def-456-789",
                "cache-control": "no-cache, no-store",
                "strict-transport-security": "max-age=31536000; includeSubDomains",
                "content-type": "text/xml;charset=UTF-8",
                "content-length": "819",
                "date": "Fri, 25 Oct 2024 20:18:14 GMT",
                "server": "AmazonEC2",
            },
            "RetryAttempts": 0,
        },
    }


@pytest.fixture
def mock_ec2_hook() -> EC2Hook:
    return mock.MagicMock(spec=EC2Hook)


@pytest.mark.parametrize(
    "instance_status_response, should_pass",
    [
        (
            _build_instance_status_response(
                "pending",
                "initializing",
                "initializing",
                "initializing",
                "initializing",
                "initializing",
                "initializing",
            ),
            False,
        ),
        (
            _build_instance_status_response(
                "running",
                "initializing",
                "ok",
                "ok",
                "initializing",
                "passed",
                "passed",
            ),
            False,
        ),
        (
            _build_instance_status_response(
                "running", "insufficient_data", "ok", "ok", "failed", "passed", "passed"
            ),
            False,
        ),
        (
            _build_instance_status_response(
                "running", "impaired", "ok", "impaired", "passed", "failed", "failed"
            ),
            False,
        ),
        (
            _build_instance_status_response(
                "running", "ok", "ok", "impaired", "passed", "passed", "failed"
            ),
            False,
        ),
        # Only pass when instance is running and all status are reachable
        (
            _build_instance_status_response(
                "running", "ok", "ok", "ok", "passed", "passed", "passed"
            ),
            True,
        ),
    ],
)
def test_wait_for_worker(instance_status_response, should_pass, mock_ec2_hook):
    mock_ec2_hook.conn.describe_instance_status.return_value = instance_status_response
    poke_return_value = wait_for_worker.function(
        environment=PRODUCTION, instance_id="i-01234abc", ec2_hook=mock_ec2_hook
    )

    assert poke_return_value.is_done == should_pass


WORKER_URL = "http://10.0.0.1:8003"


def _response(status_code, json_body=None):
    response = mock.MagicMock(status_code=status_code)
    response.json.return_value = json_body
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(str(status_code))
    return response


def test_get_worker_url():
    assert get_worker_url.function(server="10.0.0.1") == WORKER_URL


def test_trigger_reindexing_task_returns_status_url():
    data = {"model_name": "image", "start_id": 0, "end_id": 10}
    response = _response(202, {"status_check": "http://localhost:8003/task/abc-123"})
    with mock.patch("requests.post", return_value=response) as post:
        actual = trigger_reindexing_task.function(worker_url=WORKER_URL, data=data)

    post.assert_called_once_with(
        f"{WORKER_URL}/task", data=data, timeout=INDEXER_WORKER_REQUEST_TIMEOUT
    )
    assert actual == f"{WORKER_URL}/task/abc-123"


@pytest.mark.parametrize(
    "status_code, error",
    [
        pytest.param(200, ValueError, id="not-accepted"),
        pytest.param(500, requests.HTTPError, id="server-error"),
    ],
)
def test_trigger_reindexing_task_fails_unless_accepted(status_code, error):
    with mock.patch("requests.post", return_value=_response(status_code)):
        with pytest.raises(error):
            trigger_reindexing_task.function(worker_url=WORKER_URL, data={})


@pytest.mark.parametrize(
    "response, expected",
    [
        pytest.param(_response(404), False, id="task-not-found-yet"),
        pytest.param(_response(502), False, id="server-error"),
        pytest.param(
            _response(200, {"active": True, "error": False, "progress": 50}),
            False,
            id="active",
        ),
        pytest.param(
            _response(200, {"active": False, "error": False, "progress": 100}),
            True,
            id="done",
        ),
    ],
)
def test_wait_for_reindexing_task(response, expected):
    status_url = f"{WORKER_URL}/task/abc-123"
    with mock.patch("requests.get", return_value=response) as get:
        assert wait_for_reindexing_task.function(status_url=status_url) is expected

    get.assert_called_once_with(status_url, timeout=INDEXER_WORKER_REQUEST_TIMEOUT)


@pytest.mark.parametrize(
    "response, error",
    [
        pytest.param(
            _response(200, {"active": False, "error": True, "progress": 10}),
            ValueError,
            id="reindex-error",
        ),
        pytest.param(_response(403), requests.HTTPError, id="client-error"),
    ],
)
def test_wait_for_reindexing_task_raises_on_errors(response, error):
    with mock.patch("requests.get", return_value=response):
        with pytest.raises(error):
            wait_for_reindexing_task.function(status_url=f"{WORKER_URL}/task/abc")


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(requests.ConnectionError("reset"), id="connection-error"),
        pytest.param(requests.Timeout("timed out"), id="timeout"),
    ],
)
def test_wait_for_reindexing_task_retries_on_network_errors(error):
    with mock.patch("requests.get", side_effect=error):
        assert (
            wait_for_reindexing_task.function(status_url=f"{WORKER_URL}/task/abc")
            is False
        )
