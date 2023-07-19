"""
# Popularity Refresh DAG Configuration
This file defines the type for the `PopularityRefresh`, a dataclass containing
configuration for a Popularity Refresh DAG, and defines the actual
`POPULARITY_REFRESH_CONFIGS` for each of our media types. This configuration info
is used to generate the dynamic Popularity Refresh dags.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


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
    refresh_popularity_batch_timeout:  timedelta expressing the amount of time
                                       refreshing popularity scores for an individual
                                       batch of records may take.
    refresh_metrics_timeout:           timedelta expressing amount of time the
                                       refresh popularity metrics and constants
                                       may take.
    doc_md:                            str used for the DAG's documentation markdown
    """

    dag_id: str = field(init=False)
    media_type: str
    start_date: datetime = datetime(2023, 1, 1)
    # The default schedule is initially set to None while we assess the performance
    # of refreshes. The schedule will be updated in
    # https://github.com/WordPress/openverse/issues/2092
    schedule: str | None = None
    default_args: dict | None = field(default_factory=dict)

    # Initial timeouts are generous; they should be updated after assessing the
    # performance in https://github.com/WordPress/openverse/issues/2092
    refresh_popularity_batch_timeout: timedelta = timedelta(hours=1)
    refresh_metrics_timeout: timedelta = timedelta(hours=1)

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_popularity_refresh"


POPULARITY_REFRESH_CONFIGS = [
    PopularityRefresh(
        media_type="image",
        refresh_metrics_timeout=timedelta(hours=24),
    ),
    PopularityRefresh(media_type="audio"),
]
