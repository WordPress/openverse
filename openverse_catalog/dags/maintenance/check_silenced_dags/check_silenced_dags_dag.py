"""
Checks for DAGs that have silenced Slack alerts which may need to be turned back
on.

When a DAG has known failures, it can be ommitted from Slack error reporting by adding
an entry to the `silenced_slack_alerts` Airflow variable. This is a dictionary where the
key is the `dag_id` of the affected DAG, and the value is the URL of a GitHub issue
tracking the error.

The `check_silenced_alert` DAG iterates over the entries in the `silenced_slack_alerts`
configuration and verifies that the associated GitHub issues are still open. If an issue
has been closed, it is assumed that the DAG should have Slack reporting reenabled, and
an alert is sent to prompt manual update of the configuration. This prevents developers
from forgetting to reenable Slack reporting after the issue has been resolved.

The DAG runs weekly.
"""

import logging
from datetime import datetime, timedelta

from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from common.constants import DAG_DEFAULT_ARGS
from maintenance.check_silenced_dags import check_silenced_dags


logger = logging.getLogger(__name__)


DAG_ID = "check_silenced_dags"
MAX_ACTIVE = 1
GITHUB_PAT = Variable.get("GITHUB_API_KEY", default_var="not_set")


dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retry_delay": timedelta(minutes=1),
    },
    start_date=datetime(2022, 7, 29),
    schedule_interval="@weekly",
    max_active_tasks=MAX_ACTIVE,
    max_active_runs=MAX_ACTIVE,
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    tags=["maintenance"],
)

with dag:
    PythonOperator(
        task_id="check_silenced_alert_configuration",
        python_callable=check_silenced_dags.check_configuration,
        op_kwargs={
            "github_pat": GITHUB_PAT,
            "airflow_variable": "silenced_slack_alerts",
        },
    )
