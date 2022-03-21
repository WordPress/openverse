"""
This file configures the Apache Airflow DAG to (re)ingest Flickr data.
"""

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime

from common.provider_dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import flickr


DAG_ID = "flickr_workflow"

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    flickr.main,
    start_date=datetime(1970, 1, 1),
    max_active_tasks=1,
    schedule_string="@daily",
    dated=True,
    day_shift=0,
)
