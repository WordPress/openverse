"""
Iterates through open PRs in our repositories and pings assigned reviewers
who have not yet approved the PR or explicitly requested changes.

This DAG runs daily and pings on the following schedule based on priority label:

| priority | days |
| --- | --- |
| critical | 1 day |
| high | >2 days |
| medium | >4 days |
| low | >7 days |

The DAG does not ping on Saturday and Sunday and accounts for weekend days
when determining how much time has passed since the review.

Unfortunately the DAG does not know when someone is on vacation. It is up to the
author of the PR to re-assign review if one of the randomly selected reviewers
is unavailable for the time period during which the PR should be reviewed.
"""

from datetime import datetime, timedelta

from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from common.constants import DAG_DEFAULT_ARGS
from maintenance.pr_review_reminders import pr_review_reminders


DAG_ID = "pr_review_reminders"
MAX_ACTIVE_TASKS = 1
ENVIRONMENT = Variable.get("ENVIRONMENT", default_var="dev")
DRY_RUN = Variable.get("PR_REVIEW_REMINDER_DRY_RUN", default_var=(ENVIRONMENT == "dev"))
GITHUB_PAT = Variable.get("GITHUB_API_KEY", default_var="not_set")

dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retry_delay": timedelta(minutes=1),
    },
    start_date=datetime(2022, 6, 9),
    # Run every weekday
    schedule="0 0 * * 1-5",
    max_active_tasks=MAX_ACTIVE_TASKS,
    max_active_runs=MAX_ACTIVE_TASKS,
    # If this was True, airflow would run this DAG in the beginning
    # for each day from the start day to now
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    tags=["maintenance"],
)

with dag:
    PythonOperator(
        task_id="pr_review_reminder_operator",
        python_callable=pr_review_reminders.post_reminders,
        op_kwargs={"github_pat": GITHUB_PAT, "dry_run": DRY_RUN},
    )
