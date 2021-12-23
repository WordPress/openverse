# airflow DAG (necessary for Airflow to find this file)

from datetime import datetime, timedelta

from common.dag_factory import create_provider_api_workflow
from providers.provider_api_scripts import jamendo


DAG_ID = "jamendo_workflow"
DAGRUN_TIMEOUT = timedelta(hours=24)


globals()[DAG_ID] = create_provider_api_workflow(
    DAG_ID,
    jamendo.main,
    start_date=datetime(1970, 1, 1),
    max_active_tasks=1,
    schedule_string="@monthly",
    dated=False,
    dagrun_timeout=DAGRUN_TIMEOUT,
)
