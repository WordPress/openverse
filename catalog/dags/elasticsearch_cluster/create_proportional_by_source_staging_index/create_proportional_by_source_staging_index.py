import logging

from airflow.decorators import task
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchPythonHook

from common.elasticsearch import remove_excluded_index_settings


logger = logging.getLogger(__name__)


@task
def get_source_index(source_index: str, media_type: str):
    """
    Get the desired source index. If a source_index was passed in
    params, we use that; else we default to the filtered media index.
    """
    return source_index or f"{media_type}-filtered"


@task
def get_destination_index_name(
    media_type: str, current_datetime_str: str, percentage_of_prod: int
):
    """Get the desired name for the destination index."""
    percentage_str = round(percentage_of_prod * 100)

    return (
        f"{media_type}-{percentage_str}-percent-proportional"
        f"-{current_datetime_str.lower()}"
    )


@task
def get_destination_alias(media_type: str):
    return f"{media_type}-subset-by-source"


@task
def get_destination_index_config(source_config: dict, destination_index_name: str):
    """
    Build the index configuration for the destination index, based on the
    source index configuration.
    """
    destination_config = remove_excluded_index_settings(source_config)

    # Apply the desired index name
    destination_config["index"] = destination_index_name
    return destination_config


@task
def get_staging_source_counts(source_index: str, es_host: str):
    """
    Get the count of records per source for the given media type in the
    staging source index.
    """
    es_conn = ElasticsearchPythonHook(hosts=[es_host]).get_conn

    response = es_conn.search(
        index=source_index,
        size=0,
        aggregations={
            "unique_sources": {
                "terms": {"field": "source", "size": 100, "order": {"_key": "desc"}}
            }
        },
    )

    sources = (
        response.get("aggregations", {}).get("unique_sources", {}).get("buckets", [])
    )
    return {source["key"]: source["doc_count"] for source in sources}


@task
def get_proportional_source_count_kwargs(
    staging_source_counts: dict[str, int], percentage_of_prod: int
):
    """
    Return a list of kwargs for each mapped task to reindex the
    documents for each source individually.

    For each task we will have:
    * `max_docs`: The count of records for this source needed in the new
                  index in order for the source to make up the same
                  proportion of the new index as it does in the
                  source index.
    * `query`:    An elasticsearch query that will be used to restrict
                  the reindexing task to records from this source.
    """
    return [
        {
            "max_docs": round(staging_total * percentage_of_prod),
            "query": {"bool": {"filter": [{"term": {"source": source}}]}},
        }
        for source, staging_total in staging_source_counts.items()
    ]
