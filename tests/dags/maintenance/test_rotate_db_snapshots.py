import random
from datetime import datetime, timedelta
from unittest import mock

import boto3
import pytest
from maintenance.rotate_db_snapshots import delete_previous_snapshots


@pytest.fixture
def rds_client(monkeypatch):
    rds = mock.MagicMock()

    def get_client(*args, **kwargs):
        return rds

    monkeypatch.setattr(boto3, "client", get_client)
    return rds


def _make_snapshots(count: int, shuffle=False) -> dict:
    date = datetime.now()
    snaps = []
    for _id in range(count):
        date = date - timedelta(days=1)
        snaps.append(
            {
                "DBSnapshotIdentifier": _id,
                "SnapshotCreateTime": date.isoformat(),
            }
        )
    return {"DBSnapshots": snaps}


@pytest.mark.parametrize(
    ("snapshots", "snapshots_to_retain"),
    (
        # Less than 7
        (_make_snapshots(1), 2),
        (_make_snapshots(1), 5),
        # Exactly the number we want to keep
        (_make_snapshots(7), 7),
        (_make_snapshots(2), 2),
    ),
)
def test_delete_previous_snapshots_no_snapshots_to_delete(
    snapshots, snapshots_to_retain, rds_client
):
    rds_client.describe_db_snapshots.return_value = snapshots
    delete_previous_snapshots.function("fake_arn", snapshots_to_retain)
    rds_client.delete_db_snapshot.assert_not_called()


def test_delete_previous_snapshots(rds_client):
    snapshots_to_retain = 6
    snapshots = _make_snapshots(10)
    snapshots_to_delete = snapshots["DBSnapshots"][snapshots_to_retain:]
    rds_client.describe_db_snapshots.return_value = snapshots
    delete_previous_snapshots.function("fake_arn", snapshots_to_retain)
    rds_client.delete_db_snapshot.assert_has_calls(
        [
            mock.call(DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"])
            for snapshot in snapshots_to_delete
        ]
    )


def test_sorts_snapshots(rds_client):
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

    rds_client.describe_db_snapshots.return_value = snapshots
    delete_previous_snapshots.function("fake_arn", snapshots_to_retain)
    rds_client.delete_db_snapshot.assert_has_calls(
        [
            mock.call(DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"])
            for snapshot in snapshots_to_delete
        ]
    )
