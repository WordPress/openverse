"""
This file configures the Apache Airflow DAG to ingest and reingest
Flickr data according to the following strategy:

We run `flickr.main` with a number of different date parameters. For
each of these parameters, `flickr.main` should ingest the metadata
associated with photos uploaded on that date.  The dates to ingest are
calculated using the `util.helpers.get_reingestion_day_list_list`
method.
"""
# airflow DAG (necessary for Airflow to find this file)

from datetime import datetime, timedelta

from common.helpers import get_reingestion_day_list_list
from common.provider_dag_factory import create_day_partitioned_ingestion_dag
from providers.provider_api_scripts import flickr


DAG_ID = "flickr_ingestion_workflow"
START_DATE = datetime(1970, 1, 1)
INGESTION_TASK_TIMEOUT = timedelta(minutes=30)

DAILY_LIST_LENGTH = 7
WEEKLY_LIST_LENGTH = 12
FORTNIGHTLY_LIST_LENGTH = 20
ONE_MONTH_LIST_LENGTH = 24
THREE_MONTH_LIST_LENGTH = 24
SIX_MONTH_LIST_LENGTH = 40

reingestion_days = get_reingestion_day_list_list(
    (1, DAILY_LIST_LENGTH),
    (7, WEEKLY_LIST_LENGTH),
    (15, FORTNIGHTLY_LIST_LENGTH),
    (30, ONE_MONTH_LIST_LENGTH),
    (90, THREE_MONTH_LIST_LENGTH),
    (180, SIX_MONTH_LIST_LENGTH),
)

globals()[DAG_ID] = create_day_partitioned_ingestion_dag(
    DAG_ID,
    flickr.main,
    reingestion_days,
    start_date=START_DATE,
    max_active_tasks=1,
    ingestion_task_timeout=INGESTION_TASK_TIMEOUT,
)
