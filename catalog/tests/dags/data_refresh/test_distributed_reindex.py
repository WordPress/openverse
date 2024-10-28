import logging
from unittest import mock

import pytest
from airflow.providers.amazon.aws.hooks.ec2 import EC2Hook

from common.constants import PRODUCTION
from data_refresh.distributed_reindex import wait_for_worker


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
