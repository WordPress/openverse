import random
from datetime import datetime, timedelta
from unittest import mock

import pytest

from common.constants import AWS_RDS_CONN_ID
from maintenance.rotate_db_snapshots import (
    AIRFLOW_MANAGED_SNAPSHOT_ID_PREFIX,
    delete_previous_snapshots,
)


@pytest.fixture
def rds_hook(monkeypatch):
    RdsHook = mock.MagicMock()

    monkeypatch.setattr("maintenance.rotate_db_snapshots.RdsHook", RdsHook)
    return RdsHook


@pytest.fixture
def hook(rds_hook):
    hook_instance = mock.MagicMock()
    rds_hook.return_value = hook_instance
    return hook_instance


def _make_snapshots(count: int, shuffle=False) -> dict:
    date = datetime.now()
    snaps = []
    for _id in range(count):
        date = date - timedelta(days=1)
        snaps.append(
            {
                "DBSnapshotIdentifier": f"{AIRFLOW_MANAGED_SNAPSHOT_ID_PREFIX}-{_id}",
                "SnapshotCreateTime": date,  # boto3 returns datetime objects
            }
        )
    return {"DBSnapshots": snaps}


@pytest.mark.parametrize(
    ("snapshots", "snapshots_to_retain"),
    (
        # Less than the number we want to keep
        (_make_snapshots(1), 2),
        (_make_snapshots(1), 5),
        # Exactly the number we want to keep
        (_make_snapshots(7), 7),
        (_make_snapshots(2), 2),
    ),
)
def test_delete_previous_snapshots_no_snapshots_to_delete(
    snapshots, snapshots_to_retain, hook
):
    hook.conn.describe_db_snapshots.return_value = snapshots
    delete_previous_snapshots.function("fake_db_identifier", snapshots_to_retain)
    hook.conn.delete_db_snapshot.assert_not_called()


def test_delete_previous_snapshots(hook):
    snapshots_to_retain = 6
    snapshots = _make_snapshots(10)
    snapshots_to_delete = snapshots["DBSnapshots"][snapshots_to_retain:]
    hook.conn.describe_db_snapshots.return_value = snapshots

    delete_previous_snapshots.function("fake_db_identifier", snapshots_to_retain)
    hook.conn.delete_db_snapshot.assert_has_calls(
        [
            mock.call(DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"])
            for snapshot in snapshots_to_delete
        ]
    )


def test_delete_previous_snapshots_ignores_non_airflow_managed_ones(hook):
    snapshots_to_retain = 2
    snapshots = _make_snapshots(4)
    # Set the last one to an unmanaged snapshot leaving 1 to delete
    snapshots["DBSnapshots"][-1]["DBSnapshotIdentifier"] = "not-managed-by-airflow-123"
    snapshot_to_delete = snapshots["DBSnapshots"][-2]

    hook.conn.describe_db_snapshots.return_value = snapshots

    delete_previous_snapshots.function("fake_db_identifier", snapshots_to_retain)
    hook.conn.delete_db_snapshot.assert_has_calls(
        [mock.call(DBSnapshotIdentifier=snapshot_to_delete["DBSnapshotIdentifier"])]
    )


def test_sorts_snapshots(hook):
    """
    As far as we can tell the API does return them pre-sorted but it isn't documented
    so just to be sure we'll sort them anyway.
    """
    snapshots_to_retain = 6
    # _make_snapshots returns them ordered by date reversed
    snapshots = _make_snapshots(10)
    snapshots_to_delete = snapshots["DBSnapshots"][snapshots_to_retain:]
    # shuffle the snapshots to mimic an unstable API return order
    random.shuffle(snapshots["DBSnapshots"])

    hook.conn.describe_db_snapshots.return_value = snapshots
    delete_previous_snapshots.function("fake_db_identifier", snapshots_to_retain)
    hook.conn.delete_db_snapshot.assert_has_calls(
        [
            mock.call(DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"])
            for snapshot in snapshots_to_delete
        ]
    )


def test_instantiates_rds_hook_with_rds_connection_id(rds_hook, hook):
    hook.conn.describe_db_snapshots.return_value = _make_snapshots(0)

    delete_previous_snapshots.function("fake_db_identifier", 0)
    rds_hook.assert_called_once_with(aws_conn_id=AWS_RDS_CONN_ID)
