"""
This file configures the Apache Airflow DAG to (re)ingest Flickr data.
"""
import logging

# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime, timedelta

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import walters_art_museum as wam


logging.basicConfig(
    format="%(asctime)s: [%(levelname)s - DAG Loader] %(message)s", level=logging.DEBUG
)


logger = logging.getLogger(__name__)

DAG_ID = "walters_workflow"

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    wam.main,
    start_date=datetime(2020, 9, 27),
    schedule_string="@monthly",
    dated=False,
    execution_timeout=timedelta(days=1),
)
