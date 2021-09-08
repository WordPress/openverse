# airflow DAG (necessary for Airflow to find this file)
import logging
from datetime import datetime

from provider_api_scripts import wikimedia_commons
from util.dag_factory import create_provider_api_workflow


logging.basicConfig(
    format="%(asctime)s: [%(levelname)s - DAG Loader] %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

DAG_ID = "wikimedia_commons_workflow"

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    wikimedia_commons.main,
    start_date=datetime(1970, 1, 1),
    # concurrency was 3 before,
    # maybe this is the reason for frequent failures?
    concurrency=1,
    schedule_string="@monthly",
    dated=True,
)
