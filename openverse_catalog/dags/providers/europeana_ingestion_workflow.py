# airflow DAG (necessary for Airflow to find this file)

import logging
from datetime import datetime, timedelta

from common.dag_factory import create_day_partitioned_ingestion_dag
from common.helpers import get_reingestion_day_list_list
from providers.provider_api_scripts import europeana


logging.basicConfig(
    format="%(asctime)s: [%(levelname)s - DAG Loader] %(message)s", level=logging.DEBUG
)


logger = logging.getLogger(__name__)

DAG_ID = "europeana_ingestion_workflow"
START_DATE = datetime(2013, 11, 21)
INGESTION_TASK_TIMEOUT = timedelta(hours=12)

DAILY_LIST_LENGTH = 7
ONE_MONTH_LIST_LENGTH = 12
THREE_MONTH_LIST_LENGTH = 40

reingestion_days = get_reingestion_day_list_list(
    (1, DAILY_LIST_LENGTH), (30, ONE_MONTH_LIST_LENGTH), (90, THREE_MONTH_LIST_LENGTH)
)

globals()[DAG_ID] = create_day_partitioned_ingestion_dag(
    DAG_ID,
    europeana.main,
    reingestion_days,
    start_date=START_DATE,
    concurrency=3,
    ingestion_task_timeout=INGESTION_TASK_TIMEOUT,
)
