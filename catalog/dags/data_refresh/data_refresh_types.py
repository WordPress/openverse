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
    index_readiness_timeout:           timedelta expressing amount of time it may take
                                       to await a healthy ES index after reindexing
    data_refresh_poke_interval:        int number of seconds to wait between
                                       checks to see if conflicting DAGs are running.
    doc_md:                            str used for the DAG's documentation markdown
    """

    dag_id: str = field(init=False)
    filtered_index_dag_id: str = field(init=False)
    media_type: str
    start_date: datetime = datetime(2020, 1, 1)
    schedule: str | None = "0 0 * * 1"  # Mondays 00:00 UTC
    default_args: dict | None = field(default_factory=dict)
    dag_timeout: timedelta = timedelta(days=1)
    copy_data_timeout: timedelta = timedelta(hours=1)
    index_readiness_timeout: timedelta = timedelta(days=1)
    data_refresh_poke_interval: int = REFRESH_POKE_INTERVAL

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_data_refresh"
        self.filtered_index_dag_id = f"create_filtered_{self.media_type}_index"


DATA_REFRESH_CONFIGS = {
    IMAGE: DataRefreshConfig(
        media_type="image",
        dag_timeout=timedelta(days=4),
        copy_data_timeout=timedelta(hours=12),
        data_refresh_poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
    ),
    AUDIO: DataRefreshConfig(
        media_type="audio",
        data_refresh_poke_interval=int(
            os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30)
        ),
    ),
}
