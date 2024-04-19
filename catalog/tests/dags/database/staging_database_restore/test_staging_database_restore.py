from datetime import datetime, timedelta
from unittest import mock

import pytest
from airflow import DAG
from airflow.providers.amazon.aws.hooks.rds import RdsHook
from airflow.utils.trigger_rule import TriggerRule
from tests.dags.database.staging_database_restore.data import (
    DESCRIBE_DB_INSTANCES_RESPONSE,
)

from common.github import GitHubAPI
from database.staging_database_restore import staging_database_restore


REFERENCE_DATE = datetime(2021, 1, 1, 0, 0, 0)


@pytest.fixture
def mock_rds_hook() -> RdsHook:
    return mock.MagicMock(spec=RdsHook)


@pytest.fixture
def mock_github() -> GitHubAPI:
    return mock.MagicMock(spec=GitHubAPI)


@pytest.mark.parametrize("should_skip", [True, False])
def test_skip_restore(should_skip):
    with mock.patch.object(
        staging_database_restore.slack, "send_message"
    ) as mock_send_message:
        actual = staging_database_restore.skip_restore.function(should_skip)
        assert actual == (not should_skip)
        assert mock_send_message.called == should_skip


@pytest.mark.parametrize(
    "snapshots, expected",
    [
        (
            [
                {
                    "SnapshotCreateTime": REFERENCE_DATE,
                    "DBSnapshotIdentifier": str(REFERENCE_DATE),
                }
            ],
            str(REFERENCE_DATE),
        ),
        (
            [
                {
                    "SnapshotCreateTime": (d := REFERENCE_DATE - timedelta(days=days)),
                    "DBSnapshotIdentifier": str(d),
                }
                for days in range(10, 0, -1)  # Reversed so that the latest is last
            ],
            REFERENCE_DATE,
        ),
        pytest.param(
            [],
            None,
            marks=pytest.mark.raises(exception=ValueError, match="No snapshots found"),
        ),
    ],
)
def test_get_latest_prod_snapshot(snapshots, expected, mock_rds_hook):
    mock_rds_hook.conn.describe_db_snapshots.return_value = {"DBSnapshots": snapshots}
    staging_database_restore.get_latest_prod_snapshot.function(rds_hook=mock_rds_hook)


@pytest.mark.parametrize(
    "details",
    [
        [DESCRIBE_DB_INSTANCES_RESPONSE],
        # Missing keys raises a KeyError
        pytest.param([{}], marks=pytest.mark.raises(exception=KeyError)),
        # No data
        pytest.param(
            [],
            marks=pytest.mark.raises(exception=ValueError, match="No staging DB found"),
        ),
    ],
)
def test_get_staging_db_details(details, mock_rds_hook):
    mock_rds_hook.conn.describe_db_instances.return_value = {"DBInstances": details}
    actual = staging_database_restore.get_staging_db_details.function(
        rds_hook=mock_rds_hook
    )
    # Easiest way to test the logic is just to assert that it looks exactly how we
    # want after the function is called.
    assert actual == {
        "AllocatedStorage": 123,
        "AvailabilityZone": "string",
        "DBInstanceClass": "string",
        "DBSubnetGroupName": "string",
        "MultiAZ": False,
        "PubliclyAccessible": False,
        "VpcSecurityGroupIds": ["vpcsg1", "vpcsg2"],
        "CopyTagsToSnapshot": True,
    }


def test_make_rename_task_group():
    rule = TriggerRule.NONE_FAILED
    with DAG(dag_id="test_make_rename_task_group", start_date=datetime(1970, 1, 1)):
        group = staging_database_restore.make_rename_task_group("dibble", "crim", rule)
    assert group.group_id == "rename_dibble_to_crim"
    rename, await_rename = list(group)
    assert rename.task_id == "rename_dibble_to_crim.rename_dibble_to_crim"
    assert rename.trigger_rule == TriggerRule.NONE_FAILED
    assert rename.retries == 0
    assert await_rename.task_id == "rename_dibble_to_crim.await_crim"
    # This should not be affected by the trigger rule
    assert await_rename.trigger_rule == TriggerRule.ALL_SUCCESS
    assert await_rename.retries == 2


@pytest.mark.parametrize(
    "tags, expected",
    [
        (
            ["11926a78cfe8ca150fe6d232a5689141c35417d1", "latest"],
            "11926a78cfe8ca150fe6d232a5689141c35417d1",
        ),
        (
            ["rel-2023.05.30.17.57.04", "latest"],
            "rel-2023.05.30.17.57.04",
        ),
        (
            ["rel-2023.05.30.17.57.04"],
            "rel-2023.05.30.17.57.04",
        ),
        (
            [
                "11926a78cfe8ca150fe6d232a5689141c35417d1",
                "2e82df0105a94f7b85c48321fc3e05c23edc49bd",
                "latest",
            ],
            "11926a78cfe8ca150fe6d232a5689141c35417d1",
        ),
        pytest.param(
            ["11926a78cfe8ca150fe6d232a5689141c35417d1"],
            None,
            marks=pytest.mark.raises(
                exception=ValueError, match="Latest version is not"
            ),
        ),
    ],
)
def test_get_latest_api_package_version(tags, expected, mock_github):
    mock_github.get_package_versions.return_value = [
        {"metadata": {"container": {"tags": tags}}}
    ]
    actual = staging_database_restore.get_latest_api_package_version.function(
        github=mock_github
    )
    assert actual == expected
