from unittest import mock

import pytest

from common.sensors.constants import (
    PRODUCTION_ES_CONCURRENCY_TAG,
    STAGING_DB_CONCURRENCY_TAG,
)
from common.sensors.utils import get_dags_with_concurrency_tag


def test_get_dags_with_concurrency_tag_excludes_running_and_excluded_dags():
    dag = mock.MagicMock(dag_id="staging_database_restore")

    actual = get_dags_with_concurrency_tag.function(
        tag=STAGING_DB_CONCURRENCY_TAG,
        excluded_dag_ids=["staging_audio_data_refresh"],
        dag=dag,
    )

    assert actual == ["recreate_full_staging_index", "staging_image_data_refresh"]


def test_get_dags_with_concurrency_tag_requires_the_running_dag_to_have_the_tag():
    dag = mock.MagicMock(dag_id="staging_database_restore")

    with pytest.raises(ValueError, match="does not have the tag itself"):
        get_dags_with_concurrency_tag.function(
            tag=PRODUCTION_ES_CONCURRENCY_TAG, excluded_dag_ids=[], dag=dag
        )
