"""
# Data Refresh DAG Configuration
This file defines the type for the `DataRefresh`, a dataclass containing
configuation for a Data Refresh DAG, and defines the actual `DATA_REFRESH_CONFIGS`
for each of our media types. This configuration information is used to generate
the dynamic Data Refresh dags.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass
class DataRefresh:
    """
    Configuration object for a data refresh DAG.

    Required Constructor Arguments:

    media_type: string describing the media type to be refreshed.

    Optional Constructor Arguments:

    default_args:      dictionary which is passed to the airflow.dag.DAG
                       __init__ method.
    start_date:        datetime.datetime giving the
                       first valid execution_date of the DAG.
    schedule_interval: string giving the schedule on which the DAG should
                       be run.  Passed to the airflow.dag.DAG __init__
                       method.
    execution_timeout: datetime.timedelta giving the amount of time a given data
                       pull may take.
    doc_md:            string which should be used for the DAG's documentation markdown
    """

    dag_id: str = field(init=False)
    media_type: str
    start_date: datetime = datetime(2020, 1, 1)
    execution_timeout: timedelta = timedelta(hours=24)
    schedule_interval: Optional[str] = "@weekly"
    default_args: Optional[Dict] = field(default_factory=dict)

    def __post_init__(self):
        self.dag_id = f"{self.media_type}_data_refresh"


DATA_REFRESH_CONFIGS = [
    DataRefresh(
        media_type="image",
        execution_timeout=timedelta(days=3),
    ),
    DataRefresh(media_type="audio"),
]
