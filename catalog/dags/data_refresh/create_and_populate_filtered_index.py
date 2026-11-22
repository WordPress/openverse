"""
# Create and Promote Index

This file contains TaskGroups related to creating and populating the filtered Elasticsearch indices
as part of the Data Refresh.

TODO: We'll swap out the create and populate filtered index DAG to use this instead
of the one defined in the legacy_data_refresh.
"""

import logging
import uuid
from datetime import timedelta

from airflow.providers.http.operators.http import HttpOperator
from airflow.sdk import TriggerRule, task, task_group
from requests import Response

from common import elasticsearch as es
from common.constants import MediaType
from data_refresh.es_mapping import index_settings


logger = logging.getLogger(__name__)

SENSITIVE_TERMS_CONN_ID = "sensitive_terms"


def response_filter_sensitive_terms_endpoint(response: Response) -> list[str]:
    return [term.decode("utf-8").strip() for term in response.iter_lines()]


def sensitive_terms_clauses(sensitive_terms) -> list[dict]:
    """
    One `terms` query per field that may hold sensitive terms. The `.raw` subfields
    use the standard analyzer, so a term matches one lowercased word of the field.
    """
    return [
        {"terms": {f"{field}.raw": sensitive_terms}}
        for field in ["tags.name", "title", "description"]
    ]


def get_sensitive_terms() -> HttpOperator:
    return HttpOperator(
        task_id="get_sensitive_terms",
        http_conn_id=SENSITIVE_TERMS_CONN_ID,
        method="GET",
        response_check=lambda response: response.status_code == 200,
        response_filter=response_filter_sensitive_terms_endpoint,
    )


@task(trigger_rule=TriggerRule.NONE_FAILED)
def get_filtered_index_name(media_type: str, destination_index_name: str) -> str:
    # If a destination index name is explicitly passed, use it.
    if destination_index_name:
        return destination_index_name

    # Otherwise, generate an index name with a new UUID. This is useful when
    # filtered index creation is run outside of a data refresh, because it
    # avoids naming collisions when a filtered index already exists.
    logger.info("Generating new destination index name.")
    return f"{media_type}-{uuid.uuid4().hex}-filtered"


@task_group(group_id="create_and_populate_filtered_index")
def create_and_populate_filtered_index(
    es_host: str,
    media_type: MediaType,
    origin_index_name: str,
    filtered_index_name: str,
    timeout: timedelta,
    poke_interval: int,
):
    """
    Create and populate a filtered index based on the given origin index, excluding
    documents with sensitive terms.
    """
    create_filtered_index = es.create_index.override(
        trigger_rule=TriggerRule.NONE_FAILED,
    )(
        index_config={
            "index": filtered_index_name,
            "body": index_settings(media_type),
        },
        es_host=es_host,
        # A cleared run fills the index a failed attempt left, skipping the
        # documents already in it.
        exist_ok=True,
    )

    sensitive_terms = get_sensitive_terms()

    populate_filtered_index = es.trigger_and_wait_for_reindex(
        es_host=es_host,
        destination_index=filtered_index_name,
        source_index=origin_index_name,
        timeout=timeout,
        requests_per_second="{{ var.value.get('ES_INDEX_THROTTLING_RATE', 20_000) }}",
        # The number of scrolls that read the origin index in parallel. "auto" uses
        # one per shard. With fewer slices than shards, each slice still sends its
        # searches to every shard, so ES_INDEX_THROTTLING_RATE is the more direct
        # way to reduce load.
        slices="{{ var.value.get('ES_FILTERED_INDEX_REINDEX_SLICES', 'auto') }}",
        query={"bool": {"must_not": sensitive_terms_clauses(sensitive_terms.output)}},
        refresh=False,
        poke_interval=poke_interval,
    )

    refresh_index = es.refresh_index(es_host=es_host, index_name=filtered_index_name)

    # sensitive_terms >> populate_filtered_index
    create_filtered_index >> sensitive_terms >> populate_filtered_index >> refresh_index


@task_group(group_id="filter_sensitive_documents")
def filter_sensitive_documents(
    es_host: str,
    origin_index_name: str,
    filtered_index_name: str,
    timeout: timedelta,
    poke_interval: int,
):
    """
    Delete the documents with sensitive terms from a filtered index that the indexer
    workers filled with a copy of every document in the origin index.

    The filtered index must hold exactly the origin index's documents first. An
    indexer worker that doesn't know about the filtered index leaves it empty, and
    promoting that would hide every result from default searches.
    """
    sensitive_terms = get_sensitive_terms()

    refresh_before = es.refresh_index.override(task_id="refresh_before_filtering")(
        es_host=es_host, index_name=filtered_index_name
    )

    same_count = es.assert_same_document_count(
        es_host=es_host, index=origin_index_name, other_index=filtered_index_name
    )

    delete_sensitive = es.trigger_and_wait_for_delete_by_query(
        es_host=es_host,
        index=filtered_index_name,
        query={
            "bool": {
                "should": sensitive_terms_clauses(sensitive_terms.output),
                "minimum_should_match": 1,
            }
        },
        timeout=timeout,
        requests_per_second="{{ var.value.get('ES_INDEX_THROTTLING_RATE', 20_000) }}",
        poke_interval=poke_interval,
    )

    refresh_after = es.refresh_index(es_host=es_host, index_name=filtered_index_name)

    sensitive_terms >> refresh_before >> same_count >> delete_sensitive >> refresh_after
