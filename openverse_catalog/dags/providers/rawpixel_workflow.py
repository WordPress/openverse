# airflow DAG (necessary for Airflow to find this file)
import logging
from datetime import datetime

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import raw_pixel


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = "rawpixel_workflow"


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    raw_pixel.main,
    start_date=datetime(1970, 1, 1),
    max_active_tasks=1,
    schedule_string="@monthly",
    dated=False,
)
