"""
This file configures the Apache Airflow DAG to ingest NYPL data.

We do this by running `provider_api_scripts.nypl.main`
"""
# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import nypl


DAG_ID = "nypl_workflow"
START_DATE = datetime(2020, 1, 1)

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    nypl.main,
    start_date=START_DATE,
    schedule_string="@monthly",
    dated=False,
    execution_timeout=timedelta(hours=24),
)
