"""
This file configures the Apache Airflow DAG to ingest Finnish museums data.

We do this by running `provider_api_scripts.finnish_museums.main`
"""

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import finnish_museums


DAG_ID = "finnish_museums_workflow"
START_DATE = datetime(2020, 9, 1)

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    finnish_museums.main,
    start_date=START_DATE,
    schedule_string="@monthly",
    dated=False,
    execution_timeout=timedelta(hours=24),
)
