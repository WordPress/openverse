import pytest
from airflow.exceptions import AirflowException

from common.elasticsearch import raise_for_reindex_failure


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(
            {"completed": True, "response": {"total": 10, "failures": []}},
            id="succeeded",
        ),
        pytest.param({"completed": True}, id="no_response_body"),
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
    ],
)
def test_raise_for_reindex_failure_raises(response):
    with pytest.raises(AirflowException, match="Reindex failed"):
        raise_for_reindex_failure(response)
