"""
This file configures the Apache Airflow DAG to ingest and reingest
Wikimedia Commons data according to the following strategy:

We run `wikimedia_commons.main` with a number of different date
parameters. For each of these parameters, `wikimedia_commons.main`
should ingest the metadata associated with photos uploaded on that date.
The dates to ingest are calculated using the
`util.helpers.get_reingestion_day_list_list` method.
"""
# airflow DAG (necessary for Airflow to find this file)

import logging
from datetime import datetime, timedelta

from common.dag_factory import create_day_partitioned_ingestion_dag
from common.helpers import get_reingestion_day_list_list
from providers.provider_api_scripts import wikimedia_commons


logging.basicConfig(
    format="%(asctime)s: [%(levelname)s - DAG Loader] %(message)s", level=logging.DEBUG
)


logger = logging.getLogger(__name__)

DAG_ID = "wikimedia_ingestion_workflow"
START_DATE = datetime(1970, 1, 1)
INGESTION_TASK_TIMEOUT = timedelta(minutes=90)

DAILY_LIST_LENGTH = 6
ONE_MONTH_LIST_LENGTH = 9
THREE_MONTH_LIST_LENGTH = 18
SIX_MONTH_LIST_LENGTH = 30

reingestion_days = get_reingestion_day_list_list(
    (1, DAILY_LIST_LENGTH),
    (30, ONE_MONTH_LIST_LENGTH),
    (90, THREE_MONTH_LIST_LENGTH),
    (180, SIX_MONTH_LIST_LENGTH),
)

globals()[DAG_ID] = create_day_partitioned_ingestion_dag(
    DAG_ID,
    wikimedia_commons.main,
    reingestion_days,
    start_date=START_DATE,
    max_active_tasks=2,
    ingestion_task_timeout=INGESTION_TASK_TIMEOUT,
)
