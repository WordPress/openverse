# airflow DAG (necessary for Airflow to find this file)
import logging
from datetime import datetime

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import cleveland_museum_of_art


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)
DAG_ID = "cleveland_museum_workflow"


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    cleveland_museum_of_art.main,
    start_date=datetime(2020, 1, 15),
    concurrency=1,
    schedule_string="@daily",
    dated=False,
)
