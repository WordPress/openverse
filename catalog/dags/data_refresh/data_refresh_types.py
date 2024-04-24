"""
# Data Refresh DAG Configuration
This file defines the type for the `DataRefresh`, a dataclass containing
configuration for a Data Refresh DAG, and defines the actual `DATA_REFRESH_CONFIGS`.
This configuration information is used to generate the dynamic Data Refresh dags.


# TODO should we have separate configuration for each environment or should config
# be identical?
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from common.constants import AUDIO, IMAGE, REFRESH_POKE_INTERVAL


@dataclass
class DataRefreshConfig:
    """
    Configuration object for a data refresh DAG.

    Required Constructor Arguments:

    media_type: str describing the media type to be refreshed.
    #TODO maybe get rid of?
    environment: str describing the environment in which data should be refreshed.

    Optional Constructor Arguments:

    default_args:                      dictionary which is passed to the
                                       airflow.dag.DAG __init__ method.
    start_date:                        datetime.datetime giving the
                                       first valid logical date of the DAG.
    schedule:                          string giving the schedule on which the DAG
                                       should be run.  Passed to the
                                       airflow.dag.DAG __init__ method.
    data_refresh_timeout:              timedelta expressing the amount of time the data
                                       refresh (run by the ingestion server) may take.
    refresh_metrics_timeout:           timedelta expressing amount of time the
                                       refresh popularity metrics tasks may take.
    refresh_matview_timeout:           timedelta expressing amount of time the
                                       refresh of the popularity matview may take.
    create_pop_constants_view_timeout: timedelta expressing amount of time the
                                       creation of the popularity constants view
                                       may take
    create_materialized_view_timeout:  timedelta expressing amount of time the
                                       creation of the matview may take
    index_readiness_timeout:           timedelta expressing amount of time it may take
                                       to await a healthy ES index after reindexing
    doc_md:                            str used for the DAG's documentation markdown
    data_refresh_poke_interval:        int number of seconds to wait between
                                       checks to see if the batched updates have
                                       completed.
    filtered_index_poke_interval:      int number of seconds to wait between
                                       checks to see if the filtered batched updates
                                       have completed.
    """

    dag_id: str = field(init=False)
    filtered_index_dag_id: str = field(init=False)
    media_type: str
    start_date: datetime = datetime(2020, 1, 1)
    schedule: str | None = "0 0 * * 1"  # Mondays 00:00 UTC
    default_args: dict | None = field(default_factory=dict)
    data_refresh_timeout: timedelta = timedelta(days=1)
    refresh_metrics_timeout: timedelta = timedelta(hours=1)
    refresh_matview_timeout: timedelta = timedelta(hours=1)
    create_pop_constants_view_timeout: timedelta = timedelta(hours=1)
    create_materialized_view_timeout: timedelta = timedelta(hours=1)
    create_filtered_index_timeout: timedelta = timedelta(days=1)
    index_readiness_timeout: timedelta = timedelta(days=1)
    data_refresh_poke_interval: int = REFRESH_POKE_INTERVAL
    filtered_index_poke_interval: int = REFRESH_POKE_INTERVAL

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_data_refresh"
        self.filtered_index_dag_id = f"create_filtered_{self.media_type}_index"


DATA_REFRESH_CONFIGS = {
    IMAGE: DataRefreshConfig(
        media_type="image",
        data_refresh_timeout=timedelta(days=4),
        refresh_metrics_timeout=timedelta(hours=24),
        refresh_matview_timeout=timedelta(hours=72),
        create_pop_constants_view_timeout=timedelta(hours=24),
        create_materialized_view_timeout=timedelta(hours=72),
        data_refresh_poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
        filtered_index_poke_interval=int(
            os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30)
        ),
    ),
    AUDIO: DataRefreshConfig(
        media_type="audio",
        data_refresh_poke_interval=int(
            os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30)
        ),
        filtered_index_poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
    ),
}
