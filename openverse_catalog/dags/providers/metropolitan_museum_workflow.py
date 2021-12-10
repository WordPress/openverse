# airflow DAG (necessary for Airflow to find this file)
from datetime import datetime

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import metropolitan_museum_of_art


DAG_ID = "metropolitan_museum_workflow"


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    metropolitan_museum_of_art.main,
    start_date=datetime(1970, 1, 1),
    concurrency=1,
    schedule_string="@daily",
    dated=True,
)
