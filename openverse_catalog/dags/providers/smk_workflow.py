"""
This file configures the Apache Airflow DAG to ingest data for SMK, the
National Gallery of Denmark.

We do this by running `provider_api_scripts.smk.main`
"""
import logging

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from common.provider_dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import smk


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = "smk_workflow"
START_DATE = datetime(2020, 1, 1)

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    smk.main,
    start_date=START_DATE,
    schedule_string="@monthly",
    dated=False,
    execution_timeout=timedelta(hours=24),
)
