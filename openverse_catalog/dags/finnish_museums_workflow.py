"""
This file configures the Apache Airflow DAG to ingest Finnish museums data.

We do this by running `provider_api_scripts.finnish_museums.main`
"""
import logging

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from provider_api_scripts import finnish_museums
from util.dag_factory import create_provider_api_workflow


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = "finnish_museums_workflow"
START_DATE = datetime(2020, 9, 1)
DAGRUN_TIMEOUT = timedelta(hours=24)

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    finnish_museums.main,
    start_date=START_DATE,
    schedule_string="@monthly",
    dated=False,
    dagrun_timeout=DAGRUN_TIMEOUT,
)
