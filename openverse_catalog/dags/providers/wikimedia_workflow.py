# airflow DAG (necessary for Airflow to find this file)
import logging
from datetime import datetime

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import wikimedia_commons


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

DAG_ID = "wikimedia_commons_workflow"

globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    wikimedia_commons.main,
    start_date=datetime(1970, 1, 1),
    # max_active_tasks was 3 before,
    # maybe this is the reason for frequent failures?
    max_active_tasks=1,
    schedule_string="@daily",
    dated=True,
    media_types=["image", "audio"],
)
