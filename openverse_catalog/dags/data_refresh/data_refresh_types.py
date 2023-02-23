"""
# Data Refresh DAG Configuration
This file defines the type for the `DataRefresh`, a dataclass containing
configuration for a Data Refresh DAG, and defines the actual `DATA_REFRESH_CONFIGS`
for each of our media types. This configuration information is used to generate
the dynamic Data Refresh dags.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class DataRefresh:
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
    data_refresh_timeout:              int giving the amount of time in seconds a
                                       given data pull may take.
    refresh_metrics_timeout:           timedelta expressing amount of time the
                                       refresh popularity metrics tasks may take.
    refresh_matview_timeout:           timedelta expressing amount of time the
                                       refresh of the popularity matview may take.
    create_pop_constants_view_timeout: timedelta expressing amount of time the
                                       creation of the popularity constants view
                                       may take
    create_materialized_view_timeout:  timedelta expressing amount of time the
                                       creation of the matview may take
    doc_md:                            str used for the DAG's documentation markdown
    """

    dag_id: str = field(init=False)
    media_type: str
    start_date: datetime = datetime(2020, 1, 1)
    schedule: str | None = "@weekly"
    default_args: dict | None = field(default_factory=dict)
    data_refresh_timeout: int = 24 * 60 * 60  # 1 day
    refresh_metrics_timeout: timedelta = timedelta(hours=1)
    refresh_matview_timeout: timedelta = timedelta(hours=1)
    create_pop_constants_view_timeout: timedelta = timedelta(hours=1)
    create_materialized_view_timeout: timedelta = timedelta(hours=1)

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_data_refresh"


DATA_REFRESH_CONFIGS = [
    DataRefresh(
        media_type="image",
        data_refresh_timeout=3 * 24 * 60 * 60,  # 3 days,
        refresh_metrics_timeout=timedelta(hours=24),
        refresh_matview_timeout=timedelta(hours=24),
        create_pop_constants_view_timeout=timedelta(hours=8),
        create_materialized_view_timeout=timedelta(hours=5),
    ),
    DataRefresh(media_type="audio"),
]
