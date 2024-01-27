from unittest import mock

import pytest

from ingestion_server import distributed_reindex_scheduler


def test_assign_work():
    ...


def test_assign_work_workers_fail():
    mock_db = mock.MagicMock()
    mock_db.cursor.return_value.__enter__.return_value.fetchone.return_value = [100]
    with mock.patch(
        "ingestion_server.distributed_reindex_scheduler._wait_for_healthcheck"
    ) as mock_wait_for_healthcheck:
        mock_wait_for_healthcheck.return_value = False

        with pytest.raises(ValueError, match="Some workers didn't respond"):
            distributed_reindex_scheduler._assign_work(
                mock_db,
                ["worker"] * 6,
                "fake-model",
                "fake-table",
                "target-index",
            )
