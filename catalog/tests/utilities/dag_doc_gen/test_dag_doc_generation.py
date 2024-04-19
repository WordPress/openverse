from typing import NamedTuple
from unittest import mock

import pytest
from tests.dags.providers.provider_api_scripts.resources.provider_data_ingester.mock_provider_data_ingester import (
    MockProviderDataIngester,
)

from providers.provider_workflows import ProviderWorkflow
from utilities.dag_doc_gen import dag_doc_generation
from utilities.dag_doc_gen.dag_doc_generation import DagInfo


class DagMock(NamedTuple):
    # schedule_interval used here because the Dag model does not actually have a
    # schedule attribute
    schedule_interval: str | None
    doc_md: str | None
    catchup: bool
    tags: list[str]


DAG_ID = "sample_dag_123"
SAMPLE_MEDIA_TYPES = ("m1", "m2")
PROVIDER_WORKFLOW_INSTANCE = mock.MagicMock()
PROVIDER_WORKFLOW_INSTANCE.media_types = SAMPLE_MEDIA_TYPES
_MODULE = "utilities.dag_doc_gen.dag_doc_generation"


@pytest.mark.parametrize(
    "dag_id, expected_mapped_dag_id",
    [
        ("sample_dag_123", "sample_dag_123"),
        ("sample_dag_audio_123", "sample_dag_{media_type}_123"),
        ("staging_database_restore", "staging_database_restore"),
        ("wikimedia_reingestion_workflow", "wikimedia_commons_workflow"),
    ],
)
@pytest.mark.parametrize("schedule", ["@daily", None])
@pytest.mark.parametrize(
    "doc, expected_doc",
    [
        (None, None),
        ("Sample simple doc", "Sample simple doc"),
        ("# Big header", "#### Big header"),
    ],
)
@pytest.mark.parametrize(
    "tags, type_",
    [
        (None, "other"),
        ([], "other"),
        (["foo"], "foo"),
        (["foo", "bar"], "foo"),
    ],
)
@pytest.mark.parametrize(
    "provider_workflow, catchup, expected_dated",
    [
        # Dated is always equal to provider_workflow.dated
        (
            ProviderWorkflow(ingester_class=MockProviderDataIngester, dated=False),
            True,
            False,
        ),
        (
            ProviderWorkflow(ingester_class=MockProviderDataIngester, dated=False),
            False,
            False,
        ),
        (
            ProviderWorkflow(ingester_class=MockProviderDataIngester, dated=True),
            True,
            True,
        ),
        (
            ProviderWorkflow(ingester_class=MockProviderDataIngester, dated=True),
            False,
            True,
        ),
        # If ProviderWorkflow is None, fall back to the value of 'catchup'
        (None, True, True),
        (None, False, False),
    ],
)
def test_get_dags_info(
    dag_id,
    expected_mapped_dag_id,
    schedule,
    doc,
    expected_doc,
    tags,
    type_,
    provider_workflow,
    catchup,
    expected_dated,
):
    dag = DagMock(schedule_interval=schedule, doc_md=doc, catchup=catchup, tags=tags)
    expected = DagInfo(
        dag_id=dag_id,
        schedule=schedule,
        doc=expected_doc,
        dated=expected_dated,
        type_=type_,
        provider_workflow=provider_workflow,
        mapped_dag_id=expected_mapped_dag_id,
    )
    with mock.patch(f"{_MODULE}.get_provider_workflows") as provider_workflow_mock:
        provider_workflow_mock.return_value.get.return_value = provider_workflow
        actual = dag_doc_generation.get_dags_info({dag_id: dag})[0]
        assert actual == expected


@pytest.mark.parametrize(
    "dag_info, is_provider, expected",
    [
        # Most info missing
        (
            DagInfo(
                dag_id=DAG_ID,
                schedule=None,
                doc=None,
                type_="",
                dated=False,
                provider_workflow=None,
                mapped_dag_id=DAG_ID,
            ),
            False,
            """
### Special Name

| DAG ID | Schedule Interval |
| --- | --- |
| `sample_dag_123` | `None` |
""",
        ),
        # Most info present
        (
            DagInfo(
                dag_id=DAG_ID,
                schedule="@daily",
                doc="A doc does exist here",
                type_="",
                dated=False,
                provider_workflow=None,
                mapped_dag_id=DAG_ID,
            ),
            False,
            """
### Special Name

| DAG ID | Schedule Interval |
| --- | --- |
| [`sample_dag_123`](#sample_dag_123) | `@daily` |
""",
        ),
        # Provider workflow with most
        (
            DagInfo(
                dag_id=DAG_ID,
                schedule="@daily",
                doc="A doc does exist here",
                type_="",
                dated=False,
                provider_workflow=PROVIDER_WORKFLOW_INSTANCE,
                mapped_dag_id=DAG_ID,
            ),
            True,
            """
### Special Name

| DAG ID | Schedule Interval | Dated | Media Type(s) |
| --- | --- | --- | --- |
| [`sample_dag_123`](#sample_dag_123) | `@daily` | `False` | m1, m2 |
""",
        ),
        # Separate mapped DAG ID
        (
            DagInfo(
                dag_id=DAG_ID,
                schedule="@daily",
                doc="A doc does exist here",
                type_="",
                dated=False,
                provider_workflow=None,
                mapped_dag_id="something_entirely_different",
            ),
            False,
            """
### Special Name

| DAG ID | Schedule Interval |
| --- | --- |
| [`sample_dag_123`](#something_entirely_different) | `@daily` |
""",
        ),
    ],
)
def test_generate_type_subsection(dag_info, is_provider, expected):
    dag_by_doc_md = {dag_info.doc: dag_info.mapped_dag_id}
    actual = dag_doc_generation.generate_type_subsection(
        "Special Name", [dag_info], is_provider, dag_by_doc_md
    )
    assert actual.strip() == expected.strip()


def test_generate_dag_doc():
    expected = (
        dag_doc_generation.PREAMBLE
        + """\
 1. [T1](#t1)

### T1

| DAG ID | Schedule Interval |
| --- | --- |
| `a` | `None` |
| [`b`](#b) | `None` |

"""
        + dag_doc_generation.MIDAMBLE
        + """\
 1. [`b`](#b)


### `b`

this one has a doc
"""
    )
    with mock.patch(f"{_MODULE}.get_dags_info") as get_dags_info_mock:
        # Return in reverse order to ensure they show up in the correct order
        get_dags_info_mock.return_value = [
            DagInfo("b", None, "this one has a doc", "t1", False, None, "b"),
            DagInfo("a", None, None, "t1", False, None, "a"),
        ]
        actual = dag_doc_generation.generate_dag_doc()
        assert actual == expected
