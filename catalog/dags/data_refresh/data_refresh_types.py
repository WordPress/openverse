"""
# Data Refresh DAG Configuration
This file defines the type for the `DataRefresh`, a dataclass containing
configuration for a Data Refresh DAG, and defines the actual `DATA_REFRESH_CONFIGS`.
This configuration information is used to generate the dynamic Data Refresh dags.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from common.constants import AUDIO, IMAGE, REFRESH_POKE_INTERVAL
from data_refresh import queries


@dataclass
class TableMapping:
    """
    Configuration object describing how a particular table in the upstream (catalog)
    database should be mapped to its downstream (API) counterpart.

    Required Constructor Arguments:

    upstream_table_name:   Name of the table in the upstream (catalog) database.
    downstream_table_name: Name of the table in the downstream (API) database.
    tertiary_column_query: Query for setting up tertiary columns in the temporary
                           table.
    copy_data_query:       Query to use when copying data from the upstream table
                           into the downstream table.
    """

    upstream_table_name: str
    downstream_table_name: str
    tertiary_column_query: str = queries.METRIC_COLUMN_SETUP_QUERY
    copy_data_query: str = queries.ADVANCED_COPY_DATA_QUERY
    temp_table_name: str = field(init=False)
    deleted_table_name: str = field(init=False)

    def __post_init__(self):
        self.temp_table_name = f"temp_import_{self.downstream_table_name}"
        self.deleted_table_name = f"api_deleted{self.downstream_table_name}"


@dataclass
class DataRefreshConfig:
    """
    Configuration object for a data refresh DAG.

    Required Constructor Arguments:

    media_type:                str describing the media type to be refreshed.
    table_mapping:             TableMapping information for the main media table for this
                               media type
    additional_table_mappings: list of TableMapping information for any additional tables
                               that should be refreshed as part of a data refresh for this
                               media type


    Optional Constructor Arguments:

    default_args:                      dictionary which is passed to the
                                       airflow.dag.DAG __init__ method.
    start_date:                        datetime.datetime giving the
                                       first valid logical date of the DAG.
    schedule:                          string giving the schedule on which the DAG
                                       should be run.  Passed to the
                                       airflow.dag.DAG __init__ method.
    dag_timeout:                       timedelta expressing the amount of time the entire
                                       data refresh may take.
    copy_data_timeout:                 timedelta expressing the amount of time it may take to
                                       copy the upstream table into the downstream DB
    indexer_worker_timeout:            timedelta expressing the amount of time it may take for
                                       any individual indexer worker to perform its portion of
                                       the distributed reindex
    index_readiness_timeout:           timedelta expressing amount of time it may take
                                       to await a healthy ES index after reindexing
    concurrency_check_poke_interval:   int number of seconds to wait between
                                       checks to see if conflicting DAGs are running
    reindex_poke_interval:             int number of seconds to wait between checks to see if
                                       the reindexing task has completed
    doc_md:                            str used for the DAG's documentation markdown
    """

    dag_id: str = field(init=False)
    filtered_index_dag_id: str = field(init=False)
    media_type: str
    table_mapping: TableMapping
    additional_table_mappings: Optional[list[TableMapping]] = None
    start_date: datetime = datetime(2020, 1, 1)
    schedule: str | None = "0 0 * * 1"  # Mondays 00:00 UTC
    default_args: dict = field(default_factory=dict)
    dag_timeout: timedelta = timedelta(days=1)
    copy_data_timeout: timedelta = timedelta(hours=1)
    indexer_worker_timeout: timedelta = timedelta(hours=12)
    index_readiness_timeout: timedelta = timedelta(days=1)
    concurrency_check_poke_interval: int = REFRESH_POKE_INTERVAL
    reindex_poke_interval: int = REFRESH_POKE_INTERVAL

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_data_refresh"
        self.filtered_index_dag_id = f"create_filtered_{self.media_type}_index"

    def table_mappings(self) -> list[TableMapping]:
        """Return the complete list of all table mappings for this media type."""
        if not self.additional_table_mappings:
            return [self.table_mapping]

        return [self.table_mapping] + self.additional_table_mappings


DATA_REFRESH_CONFIGS = {
    IMAGE: DataRefreshConfig(
        media_type=IMAGE,
        table_mapping=TableMapping(
            upstream_table_name=IMAGE,
            downstream_table_name=IMAGE,
            tertiary_column_query=queries.TIMESTAMP_COLUMN_SETUP_QUERY,
        ),
        dag_timeout=timedelta(days=4),
        copy_data_timeout=timedelta(hours=12),
        concurrency_check_poke_interval=int(
            os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)
        ),
        reindex_poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
    ),
    AUDIO: DataRefreshConfig(
        media_type=AUDIO,
        table_mapping=TableMapping(
            upstream_table_name=AUDIO,
            downstream_table_name=AUDIO,
            tertiary_column_query=queries.TIMESTAMP_COLUMN_SETUP_QUERY,
        ),
        additional_table_mappings=[
            TableMapping(
                upstream_table_name="audioset_view",
                downstream_table_name="audioset",
                # Do not set up standardized popularity column for audioset_view
                tertiary_column_query=queries.TIMESTAMP_COLUMN_SETUP_QUERY,
                # Do not check for entries in the DeletedMedia table for audioset_view
                copy_data_query=queries.BASIC_COPY_DATA_QUERY,
            ),
        ],
        concurrency_check_poke_interval=int(
            os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30)
        ),
        reindex_poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
    ),
}
