from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException
from airflow.utils.state import TaskInstanceState

from common.constants import OPENLEDGER_API_CONN_ID
from legacy_data_refresh.data_refresh_task_factory import drop_temp_tables


TRIGGER_TASK_ID = "data_refresh.ingest_upstream.trigger_ingest_upstream"


def _patch_trigger_state(state):
    task_states = {} if state is None else {TRIGGER_TASK_ID: state}
    return mock.patch(
        "legacy_data_refresh.data_refresh_task_factory.dag_state.get_task_states",
        return_value=task_states,
    )


@pytest.mark.parametrize(
    "media_type, expected_statements",
    [
        ("image", ["DROP TABLE IF EXISTS temp_import_image;"]),
        (
            "audio",
            [
                "DROP TABLE IF EXISTS temp_import_audio;",
                "DROP TABLE IF EXISTS temp_import_audioset;",
            ],
        ),
    ],
)
def test_drop_temp_tables_drops_tables_after_ingest_was_triggered(
    media_type, expected_statements
):
    dag_run = mock.MagicMock()

    with (
        _patch_trigger_state("success") as get_task_states,
        mock.patch(
            "legacy_data_refresh.data_refresh_task_factory.PostgresHook"
        ) as hook_cls,
    ):
        drop_temp_tables.function(media_type, TRIGGER_TASK_ID, dag_run=dag_run)

    get_task_states.assert_called_once_with(dag_run)
    hook_cls.assert_called_once_with(postgres_conn_id=OPENLEDGER_API_CONN_ID)
    hook_cls.return_value.run.assert_called_once_with(expected_statements)


@pytest.mark.parametrize(
    "trigger_state",
    [
        pytest.param(None, id="trigger-task-missing"),
        pytest.param(TaskInstanceState.UPSTREAM_FAILED, id="upstream-failed"),
        pytest.param(TaskInstanceState.FAILED, id="trigger-failed"),
        pytest.param("running", id="trigger-running"),
    ],
)
def test_drop_temp_tables_skips_when_ingest_was_not_triggered(trigger_state):
    with (
        _patch_trigger_state(trigger_state),
        mock.patch(
            "legacy_data_refresh.data_refresh_task_factory.PostgresHook"
        ) as hook_cls,
    ):
        with pytest.raises(AirflowSkipException):
            drop_temp_tables.function(
                "image", TRIGGER_TASK_ID, dag_run=mock.MagicMock()
            )

    hook_cls.assert_not_called()
