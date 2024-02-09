from unittest import mock

import pook
import pytest

from ingestion_server import distributed_reindex_scheduler


@pytest.mark.parametrize(
    "estimated_records, record_limit, workers, expected_ranges",
    [
        # One worker
        (100, 1000, ["worker1"], [(0, 100)]),
        # Multiple workers, even split
        (100, 1000, ["worker1", "worker2"], [(0, 50), (50, 100)]),
        # Multiple workers, uneven split
        # NOTE: records get dropped in this case
        (100, 1000, ["worker1", "worker2", "worker3"], [(0, 33), (33, 66), (66, 99)]),
        # One worker, limited
        (100, 55, ["worker1"], [(0, 55)]),
        # Two workers, limited
        (100, 50, ["worker1", "worker2"], [(0, 25), (25, 50)]),
    ],
)
def test_assign_work(estimated_records, record_limit, workers, expected_ranges):
    # Checks for the parameters
    assert len(workers) == len(
        expected_ranges
    ), "Number of workers and expected ranges do not match, correct the test parameters"
    # Set up database mock response
    mock_db = mock.MagicMock()
    mock_db.cursor.return_value.__enter__.return_value.fetchone.return_value = [
        estimated_records
    ]
    # Enable pook & mock other internal functions
    with pook.use(), mock.patch(
        "ingestion_server.distributed_reindex_scheduler.get_record_limit"
    ) as mock_get_record_limit, mock.patch(
        "ingestion_server.distributed_reindex_scheduler._wait_for_healthcheck"
    ) as mock_wait_for_healthcheck:
        mock_wait_for_healthcheck.return_value = True
        mock_get_record_limit.return_value = record_limit

        # Set up pook matches
        for worker, (start_id, end_id) in zip(workers, expected_ranges):
            pook.post(f"http://{worker}:8002/indexing_task").json(
                {
                    "model_name": "sample_model",
                    "table_name": "sample_table",
                    "target_index": "sample_index",
                    "start_id": start_id,
                    "end_id": end_id,
                }
            )

        distributed_reindex_scheduler._assign_work(
            mock_db,
            workers,
            "sample_model",
            "sample_table",
            "sample_index",
        )

        # Raise an exception to ensure all pook requests were matched
        assert pook.isdone()


def test_assign_work_workers_fail():
    mock_db = mock.MagicMock()
    mock_db.cursor.return_value.__enter__.return_value.fetchone.return_value = [100]
    with mock.patch(
        "ingestion_server.distributed_reindex_scheduler._wait_for_healthcheck"
    ) as mock_wait_for_healthcheck, pook.use(False):
        mock_wait_for_healthcheck.return_value = False

        with pytest.raises(ValueError, match="Some workers didn't respond"):
            distributed_reindex_scheduler._assign_work(
                mock_db,
                ["worker"] * 6,
                "fake-model",
                "fake-table",
                "target-index",
            )
