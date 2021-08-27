"""
This file configures the Apache Airflow DAG to (re)ingest Healthcheck data.
"""
# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime
import logging

from provider_api_scripts import healthcheck
from util.dag_factory import create_provider_api_workflow


logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - DAG Loader] %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

DAG_ID = "healthcheck_workflow"

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    healthcheck.main,
    start_date=datetime(1970, 1, 1),
    concurrency=1,
    schedule_string=None,  # only run this manually
    dated=False,
)
