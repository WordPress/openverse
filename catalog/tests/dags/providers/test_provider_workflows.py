from datetime import timedelta
from unittest import mock

import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    MockAudioOnlyProviderDataIngester,
    MockImageOnlyProviderDataIngester,
    MockProviderDataIngester,
)
from providers.provider_workflows import ProviderWorkflow, get_time_override


@pytest.mark.parametrize(
    "provider_workflow, expected_dag_id",
    [
        # If the ProviderWorkflow defines dag_id, this should be used
        (
            ProviderWorkflow(
                ingester_class=MockProviderDataIngester, dag_id="my_dag_id_override"
            ),
            "my_dag_id_override",
        ),
        # If no dag_id is defined, it should build a default using the module
        # name of the ingester class
        (
            ProviderWorkflow(ingester_class=MockProviderDataIngester),
            "mock_provider_data_ingester_workflow",
        ),
    ],
)
def test_dag_id(provider_workflow, expected_dag_id):
    assert provider_workflow.dag_id == expected_dag_id


@pytest.mark.parametrize(
    "ingester_class, expected_media_types",
    [
        (
            MockAudioOnlyProviderDataIngester,
            [
                "audio",
            ],
        ),
        (
            MockImageOnlyProviderDataIngester,
            [
                "image",
            ],
        ),
        (MockProviderDataIngester, ["audio", "image"]),
    ],
)
def test_sets_media_types(ingester_class, expected_media_types):
    provider_workflow = ProviderWorkflow(ingester_class=ingester_class)

    assert provider_workflow.media_types == expected_media_types


@pytest.mark.parametrize(
    "configuration_overrides, expected_overrides",
    [
        # No overrides configured
        ({}, []),
        # Overrides configured, but not for this dag_id
        (
            {
                "some_other_dag_id": [
                    {"task_id_pattern": "some_task_id", "timeout": "1:0:0:0"}
                ]
            },
            [],
        ),
        # Configured overrides
        (
            {
                "some_other_dag_id": [
                    {"task_id_pattern": "some_task_id", "timeout": "1:0:0:0"},
                ],
                "my_dag_id": [
                    {"task_id_pattern": "my_dag_id", "timeout": "1:2:3:4"},
                ],
            },
            [
                {"task_id_pattern": "my_dag_id", "timeout": "1:2:3:4"},
            ],
        ),
    ],
)
def test_overrides(configuration_overrides, expected_overrides):
    with mock.patch("providers.provider_workflows.Variable") as MockVariable:
        MockVariable.get.side_effect = [
            configuration_overrides,
            MockVariable.get_original()[0],
        ]
        test_workflow = ProviderWorkflow(
            dag_id="my_dag_id",
            ingester_class=MockProviderDataIngester,
            pull_timeout=timedelta(days=1),
            upsert_timeout=timedelta(hours=1),
        )

        assert test_workflow.overrides == expected_overrides


@pytest.mark.parametrize(
    "time_str, expected_timedelta",
    [
        ("0d:0h:0m:10s", timedelta(seconds=10)),
        ("30d:10h:57m:45s", timedelta(days=30, hours=10, minutes=57, seconds=45)),
        ("0d:6h:0m:0s", timedelta(hours=6)),
        ("0d:36h:0m:0s", timedelta(days=1, hours=12)),
        # Strings that do not provide all four parts
        ("0d:1h:2m", timedelta(hours=1, minutes=2)),
        ("2h", timedelta(hours=2)),
        ("10s", timedelta(seconds=10)),
        ("1d:1s", timedelta(days=1, seconds=1)),
        ("36h", timedelta(days=1, hours=12)),
        ("4s:3m:2h:1d", timedelta(days=1, hours=2, minutes=3, seconds=4)),
        # Incorrectly formatted strings returns None
        ("1d:2h:3m:4ss", None),
        ("10b", None),
        ("oned:2h:3m:4s", None),
        ("foo", None),
        (None, None),
    ],
)
def test_get_timedelta(time_str, expected_timedelta):
    actual_timedelta = get_time_override(time_str)
    assert actual_timedelta == expected_timedelta
