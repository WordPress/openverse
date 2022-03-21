"""
This file configures the Apache Airflow DAG to ingest Brooklyn museum data.

We do this by running `provider_api_scripts.brooklyn_museum.main`
"""
# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from common.provider_dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import brooklyn_museum


DAG_ID = "brooklyn_museum_workflow"
START_DATE = datetime(2020, 1, 1)

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    brooklyn_museum.main,
    start_date=START_DATE,
    schedule_string="@monthly",
    dated=False,
    execution_timeout=timedelta(hours=24),
)
