# airflow DAG (necessary for Airflow to find this file)

import logging
from datetime import datetime

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import jamendo


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

DAG_ID = "jamendo_workflow"


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    jamendo.main,
    start_date=datetime(1970, 1, 1),
    concurrency=1,
    schedule_string="@monthly",
    dated=False,
)
