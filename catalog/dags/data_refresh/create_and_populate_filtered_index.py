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

from airflow.decorators import task, task_group
from airflow.providers.http.operators.http import HttpOperator
from airflow.utils.trigger_rule import TriggerRule
from requests import Response

from common import elasticsearch as es
from common.constants import MediaType
from data_refresh.es_mapping import index_settings


logger = logging.getLogger(__name__)

SENSITIVE_TERMS_CONN_ID = "sensitive_terms"


def response_filter_sensitive_terms_endpoint(response: Response) -> list[str]:
    return [term.decode("utf-8").strip() for term in response.iter_lines()]


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
    timeout: timedelta,
    destination_index_name: str | None = None,
):
    """
    Create and populate a filtered index based on the given origin index, excluding
    documents with sensitive terms.
    """
    filtered_index_name = get_filtered_index_name(
        media_type=media_type, destination_index_name=destination_index_name
    )

    create_filtered_index = es.create_index.override(
        trigger_rule=TriggerRule.NONE_FAILED,
    )(
        index_config={
            "index": filtered_index_name,
            "body": index_settings(media_type),
        },
        es_host=es_host,
    )

    sensitive_terms = HttpOperator(
        task_id="get_sensitive_terms",
        http_conn_id=SENSITIVE_TERMS_CONN_ID,
        method="GET",
        response_check=lambda response: response.status_code == 200,
        response_filter=response_filter_sensitive_terms_endpoint,
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    populate_filtered_index = es.trigger_and_wait_for_reindex(
        es_host=es_host,
        destination_index=filtered_index_name,
        source_index=origin_index_name,
        timeout=timeout,
        requests_per_second="{{ var.value.get('ES_INDEX_THROTTLING_RATE', 20_000) }}",
        query={
            "bool": {
                "must_not": [
                    # Use `terms` query for exact matching against unanalyzed raw fields
                    {"terms": {f"{field}.raw": sensitive_terms.output}}
                    for field in ["tags.name", "title", "description"]
                ]
            }
        },
        refresh=False,
    )

    refresh_index = es.refresh_index(es_host=es_host, index_name=filtered_index_name)

    sensitive_terms >> populate_filtered_index
    create_filtered_index >> populate_filtered_index >> refresh_index

    return filtered_index_name
