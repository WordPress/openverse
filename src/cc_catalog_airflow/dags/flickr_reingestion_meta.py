"""
This file configures the Apache Airflow meta-DAG to ingest and reingest
Flickr data.
"""
# airflow DAG (necessary for Airflow to find this file)

from datetime import datetime
import logging

from provider_api_scripts import flickr
from util.dag_factory import create_day_partitioned_reingestion_meta_dag
from util.helpers import get_reingestion_day_list_list

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - DAG Loader] %(message)s',
    level=logging.DEBUG)


logger = logging.getLogger(__name__)

DAG_ID = 'flickr_meta_workflow'
START_DATE = datetime(1970, 1, 1)

ONE_MONTH_LIST_LENGTH = 24
THREE_MONTH_LIST_LENGTH = 36
SIX_MONTH_LIST_LENGTH = 48

reingestion_days = get_reingestion_day_list_list(
    (30, ONE_MONTH_LIST_LENGTH),
    (90, THREE_MONTH_LIST_LENGTH),
    (180, SIX_MONTH_LIST_LENGTH)
)

globals()[DAG_ID] = create_day_partitioned_reingestion_meta_dag(
    DAG_ID,
    flickr.main,
    reingestion_days,
    start_date=START_DATE,
    concurrency=1
)
