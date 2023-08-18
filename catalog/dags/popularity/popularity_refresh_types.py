"""
# Popularity Refresh DAG Configuration
This file defines the type for the `PopularityRefresh`, a dataclass containing
configuration for a Popularity Refresh DAG, and defines the actual
`POPULARITY_REFRESH_CONFIGS` for each of our media types. This configuration info
is used to generate the dynamic Popularity Refresh dags.
"""
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from common.constants import REFRESH_POKE_INTERVAL


@dataclass
class PopularityRefresh:
    """
    Configuration object for a popularity refresh DAG.

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
    refresh_popularity_timeout:        timedelta expressing amount of time the entire
                                       popularity refresh batched update may take.
    refresh_popularity_batch_timeout:  timedelta expressing the amount of time
                                       refreshing popularity scores for an individual
                                       batch of records may take.
    refresh_metrics_timeout:           timedelta expressing amount of time the
                                       refresh popularity metrics and constants
                                       may take.
    poke_interval:                     int number of seconds to wait between
                                       checks to see if the batched updates have
                                       completed.
    """

    dag_id: str = field(init=False)
    media_type: str
    default_args: dict | None = field(default_factory=dict)
    start_date: datetime = datetime(2023, 1, 1)
    schedule: str | None = "@monthly"
    refresh_popularity_timeout: timedelta = timedelta(days=14)
    refresh_popularity_batch_timeout: timedelta = timedelta(minutes=5)
    refresh_metrics_timeout: timedelta = timedelta(hours=1)
    poke_interval: int = REFRESH_POKE_INTERVAL

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_popularity_refresh"


POPULARITY_REFRESH_CONFIGS = [
    PopularityRefresh(
        media_type="image",
        refresh_metrics_timeout=timedelta(hours=24),
    ),
    PopularityRefresh(
        media_type="audio",
        # Poke every minute, instead of every thirty minutes
        poke_interval=int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60)),
        refresh_popularity_timeout=timedelta(days=1),
    ),
]
