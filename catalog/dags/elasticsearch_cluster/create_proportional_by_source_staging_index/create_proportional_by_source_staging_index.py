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
def get_production_source_counts(source_index: str, es_host: str):
    """
    Get the count of records per source for the given media type in the
    production source index.
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
    production_source_counts: dict[str, int], percentage_of_prod: int
):
    """
    Return a list of kwargs for each mapped task to reindex the
    documents for each source individually.

    For each task we will have:
    * `max_docs`: The count of records for this source needed in the new
                  index in order for the source to make up the same
                  proportion of the new index as it does in the
                  production unfiltered media index.
    * `query`:    An elasticsearch query that will be used to restrict
                  the reindexing task to records from this source.
    """
    # Given the record counts for each source in production, determine
    # what proportion of the production total each source represents
    production_total = sum(production_source_counts.values())
    production_source_proportions = {
        source: production_count / production_total
        for source, production_count in production_source_counts.items()
    }

    # The total number of records in the proportional subset index. Note that
    # the final count of the subset may be different if the proportions do not
    # divide evenly into the desired total, because we must round to the nearest
    # integer.
    # For example, if the desired index size is 1,000 records but each of the
    # sources must represent 1/3 of the index, we will round the count for each
    # source to 333 and have a final index with only 999 records.
    subset_total = round(production_total * percentage_of_prod)

    # Return a list of kwargs that will be passed to the mapped reindex
    # tasks, for reindexing each source into the new index.
    return [
        {
            "max_docs": round(subset_total * source_proportion),
            "query": {"bool": {"filter": [{"term": {"source": source}}]}},
        }
        for source, source_proportion in production_source_proportions.items()
    ]
