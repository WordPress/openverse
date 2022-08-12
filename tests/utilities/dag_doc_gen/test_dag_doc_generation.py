from typing import NamedTuple
from unittest import mock

import pytest

from openverse_catalog.utilities.dag_doc_gen import dag_doc_generation
from openverse_catalog.utilities.dag_doc_gen.dag_doc_generation import DagInfo


class DagMock(NamedTuple):
    schedule_interval: str | None
    doc_md: str | None
    catchup: bool
    tags: list[str]


DAG_ID = "sample_dag_123"
SAMPLE_MEDIA_TYPES = ("m1", "m2")
PROVIDER_WORKFLOW_INSTANCE = mock.MagicMock()
PROVIDER_WORKFLOW_INSTANCE.media_types = SAMPLE_MEDIA_TYPES
_MODULE = "openverse_catalog.utilities.dag_doc_gen.dag_doc_generation"


@pytest.mark.parametrize("schedule_interval", ["@daily", None])
@pytest.mark.parametrize(
    "doc, expected_doc",
    [
        (None, None),
        ("Sample simple doc", "Sample simple doc"),
        ("# Big header", "### Big header"),
    ],
)
@pytest.mark.parametrize("catchup", [True, False])
@pytest.mark.parametrize(
    "tags, type_",
    [
        (None, "other"),
        ([], "other"),
        (["foo"], "foo"),
        (["foo", "bar"], "foo"),
    ],
)
@pytest.mark.parametrize("provider_workflow", ["foo_bar", None])
def test_get_dags_info(
    schedule_interval, doc, expected_doc, catchup, tags, type_, provider_workflow
):
    dag = DagMock(
        schedule_interval=schedule_interval, doc_md=doc, catchup=catchup, tags=tags
    )
    expected = DagInfo(
        dag_id=DAG_ID,
        schedule=schedule_interval,
        doc=expected_doc,
        dated=catchup,
        type_=type_,
        provider_workflow=provider_workflow,
    )
    with mock.patch(f"{_MODULE}.get_provider_workflows") as provider_workflow_mock:
        provider_workflow_mock.return_value.get.return_value = provider_workflow
        actual = dag_doc_generation.get_dags_info({DAG_ID: dag})[0]
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
            ),
            False,
            """
## Special Name

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
            ),
            False,
            """
## Special Name

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
            ),
            True,
            """
## Special Name

| DAG ID | Schedule Interval | Dated | Media Type(s) |
| --- | --- | --- | --- |
| [`sample_dag_123`](#sample_dag_123) | `@daily` | `False` | m1, m2 |
""",
        ),
    ],
)
def test_generate_type_subsection(dag_info, is_provider, expected):
    actual = dag_doc_generation.generate_type_subsection(
        "Special Name", [dag_info], is_provider
    )
    assert actual.strip() == expected.strip()


def test_generate_dag_doc():
    expected = (
        dag_doc_generation.PREAMBLE
        + """\
 1. [T1](#t1)

## T1

| DAG ID | Schedule Interval |
| --- | --- |
| `a` | `None` |
| [`b`](#b) | `None` |

"""
        + dag_doc_generation.MIDAMBLE
        + """\
 1. [`b`](#b)


## `b`

this one has a doc
"""
    )
    with (mock.patch(f"{_MODULE}.get_dags_info") as get_dags_info_mock,):
        # Return in reverse order to ensure they show up in the correct order
        get_dags_info_mock.return_value = [
            DagInfo("b", None, "this one has a doc", "t1", False, None),
            DagInfo("a", None, None, "t1", False, None),
        ]
        actual = dag_doc_generation.generate_dag_doc()
        assert actual == expected
