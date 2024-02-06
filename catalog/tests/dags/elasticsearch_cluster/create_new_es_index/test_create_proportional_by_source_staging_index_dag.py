import pytest

from elasticsearch_cluster.create_proportional_by_source_staging_index.create_proportional_by_source_staging_index import (
    get_proportional_source_count_kwargs,
)


@pytest.mark.parametrize(
    "production_source_counts, percentage_of_prod, expected_results",
    [
        (
            {"jamendo": 10_000, "freesound": 20_000, "wikimedia_audio": 10_000},
            0.25,
            [
                {
                    "max_docs": 2_500,
                    "query": {"term": {"source.keyword": "jamendo"}},
                },
                {
                    "max_docs": 5_000,
                    "query": {"term": {"source.keyword": "freesound"}},
                },
                {
                    "max_docs": 2_500,
                    "query": {"term": {"source.keyword": "wikimedia_audio"}},
                },
            ],
        ),
        (
            {
                "jamendo": 10_000,
                "freesound": 20_000,
            },
            0.0,
            [
                {
                    "max_docs": 0,
                    "query": {"term": {"source.keyword": "jamendo"}},
                },
                {
                    "max_docs": 0,
                    "query": {"term": {"source.keyword": "freesound"}},
                },
            ],
        ),
        (
            {
                "jamendo": 982,
                "freesound": 423,
            },
            1.0,
            [
                {
                    "max_docs": 982,
                    "query": {"term": {"source.keyword": "jamendo"}},
                },
                {
                    "max_docs": 423,
                    "query": {"term": {"source.keyword": "freesound"}},
                },
            ],
        ),
        # Proportions do not divide evenly into the estimated new index total.
        (
            # All sources are exactly 1/3 of the index
            {"flickr": 3_333, "stocksnap": 3_333, "smk": 3_333},
            0.5,
            [
                {
                    # Note that each source gets 1_667 records (because it is
                    # rounded up), for a total of 5_001 records in the new index.
                    "max_docs": 1_667,
                    "query": {"term": {"source.keyword": "flickr"}},
                },
                {
                    "max_docs": 1_667,
                    "query": {"term": {"source.keyword": "stocksnap"}},
                },
                {
                    "max_docs": 1_667,
                    "query": {"term": {"source.keyword": "smk"}},
                },
            ],
        ),
        (
            "Updated {count} records",
            2,
            "Updated 2 records",
        ),
        (
            "A message without a count",
            None,
            "A message without a count",
        ),
    ],
)
def test_get_proportional_source_count_kwargs(
    production_source_counts, percentage_of_prod, expected_results
):
    actual_results = get_proportional_source_count_kwargs(
        production_source_counts, percentage_of_prod
    )
    assert actual_results == expected_results
