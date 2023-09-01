from datetime import timedelta
from unittest import mock

import pytest
from airflow.models import DagRun
from airflow.models.dag import DAG
from airflow.utils.session import create_session
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType
from popularity.dag_factory import get_providers_update_confs
from popularity.popularity_refresh_types import PopularityRefresh

from catalog.tests.test_utils.sql import POSTGRES_CONN_ID


TEST_DAG_ID = "popularity_refresh_dag_factory_test_dag"
TEST_DAG = DAG(TEST_DAG_ID, default_args={"owner": "airflow"})
TEST_DAY = datetime(2023, 1, 1)


@pytest.fixture(autouse=True)
def clean_db():
    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == TEST_DAG_ID).delete()


def _create_dagrun(start_date, dag_state, conf={}):
    return TEST_DAG.create_dagrun(
        start_date=start_date,
        execution_date=start_date,
        data_interval=(start_date, start_date),
        state=dag_state,
        run_type=DagRunType.MANUAL,
        conf=conf,
    )


@pytest.mark.parametrize(
    "providers, media_type, expected_confs",
    [
        # No providers for this media type
        ([], "image", []),
        (
            ["foo_provider"],
            "image",
            [
                {
                    "query_id": "foo_provider_popularity_refresh_20230101",
                    "table_name": "image",
                    "select_query": "WHERE provider='foo_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET standardized_popularity = standardized_image_popularity(image.provider, image.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
            ],
        ),
        (
            ["my_provider", "your_provider"],
            "audio",
            [
                {
                    "query_id": "my_provider_popularity_refresh_20230101",
                    "table_name": "audio",
                    "select_query": "WHERE provider='my_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET standardized_popularity = standardized_audio_popularity(audio.provider, audio.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
                {
                    "query_id": "your_provider_popularity_refresh_20230101",
                    "table_name": "audio",
                    "select_query": "WHERE provider='your_provider' AND updated_on < '2023-01-01 00:00:00'",
                    "update_query": "SET standardized_popularity = standardized_audio_popularity(audio.provider, audio.meta_data)",
                    "batch_size": 10000,
                    "update_timeout": 3600.0,
                    "dry_run": False,
                    "resume_update": False,
                },
            ],
        ),
    ],
)
def test_get_providers_update_confs(providers, media_type, expected_confs):
    with mock.patch(
        "common.popularity.sql.get_providers_with_popularity_data_for_media_type",
        return_value=providers,
    ):
        actual_confs = get_providers_update_confs.function(
            POSTGRES_CONN_ID,
            PopularityRefresh(
                media_type=media_type,
                refresh_popularity_batch_timeout=timedelta(hours=1),
            ),
            TEST_DAY,
        )

        assert actual_confs == expected_confs
