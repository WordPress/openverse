"""
This file configures the Apache Airflow DAG to (re)ingest Europeana data.
"""

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime

from common.provider_dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import europeana


DAG_ID = "europeana_workflow"


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    europeana.main,
    start_date=datetime(1970, 1, 1),
    max_active_tasks=1,
    schedule_string="@daily",
    dated=True,
    day_shift=0,
)
