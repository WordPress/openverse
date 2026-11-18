import pytest
from airflow.exceptions import AirflowFailException

from common.elasticsearch import raise_for_reindex_failure


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(
            {"completed": True, "response": {"total": 10, "failures": []}},
            id="succeeded",
        ),
        pytest.param({"completed": True}, id="no_response_body"),
        pytest.param(
            {"completed": True, "response": {"canceled": "", "timed_out": False}},
            id="not_canceled_or_timed_out",
        ),
    ],
)
def test_raise_for_reindex_failure_passes(response):
    raise_for_reindex_failure(response)


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(
            {
                "completed": True,
                "error": {
                    "type": "search_phase_execution_exception",
                    "reason": "No search context found for id [42]",
                },
            },
            id="task_error",
        ),
        pytest.param(
            {
                "completed": True,
                "response": {
                    "total": 10,
                    "failures": [{"index": "dest", "id": "1", "status": 400}],
                },
            },
            id="document_failures",
        ),
        pytest.param(
            {
                "completed": True,
                "response": {"failures": [], "canceled": "by user request"},
            },
            id="canceled",
        ),
        pytest.param(
            {"completed": True, "response": {"failures": [], "timed_out": True}},
            id="timed_out",
        ),
    ],
)
def test_raise_for_reindex_failure_raises(response):
    with pytest.raises(AirflowFailException, match="Reindex failed"):
        raise_for_reindex_failure(response)
