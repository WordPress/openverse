"""
# Silenced DAGs check

Check for DAGs that have silenced Slack alerts which may need to be turned back on.

When a DAG has known failures, it can be ommitted from Slack error reporting by adding
an entry to the `SILENCED_SLACK_NOTIFICATIONS` Airflow variable. This is a dictionary
where thekey is the `dag_id` of the affected DAG, and the value is a list of
SilencedSlackNotifications (which map silenced notifications to GitHub URLs) for that
DAG.

The `check_silenced_dags` DAG iterates over the entries in the
`SILENCED_SLACK_NOTIFICATIONS` configuration and verifies that the associated GitHub
issues are still open. If an issue has been closed, it is assumed that the DAG should
have Slack reporting reenabled, and an alert is sent to prompt manual update of the
configuration. This prevents developers from forgetting to reenable Slack reporting
after the issue has been resolved.

The DAG runs weekly.
"""

import logging
from datetime import datetime, timedelta

from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from common.constants import DAG_DEFAULT_ARGS
from common.github import GitHubAPI
from common.slack import SilencedSlackNotification, send_alert


logger = logging.getLogger(__name__)


DAG_ID = "check_silenced_dags"
MAX_ACTIVE = 1


def get_issue_info(issue_url: str) -> tuple[str, str, str]:
    """Parse out the owner, repo, and issue_number from a GitHub issue url."""
    url_split = issue_url.split("/")
    if len(url_split) < 4:
        raise AirflowException(f"Issue url {issue_url} could not be parsed.")
    return url_split[-4], url_split[-3], url_split[-1]


def get_dags_with_closed_issues(
    github_pat: str, silenced_dags: dict[str, list[SilencedSlackNotification]]
):
    gh = GitHubAPI(github_pat)

    dags_to_reenable = []
    for dag_id, silenced_notifications in silenced_dags.items():
        for notification in silenced_notifications:
            issue_url = notification["issue"]
            owner, repo, issue_number = get_issue_info(issue_url)
            github_issue = gh.get_issue(repo, issue_number, owner)

            if github_issue.get("state") == "closed":
                # If the associated issue has been closed, this DAG can have
                # alerting reenabled for this predicate.
                dags_to_reenable.append((dag_id, issue_url, notification["predicate"]))
    return dags_to_reenable


def check_configuration(github_pat: str):
    silenced_dags = Variable.get(
        "SILENCED_SLACK_NOTIFICATIONS", default_var={}, deserialize_json=True
    )
    dags_to_reenable = get_dags_with_closed_issues(github_pat, silenced_dags)

    if not dags_to_reenable:
        raise AirflowSkipException(
            "All DAGs configured to silence messages have work still in progress."
            " No configuration updates needed."
        )

    message = (
        "The following DAGs have Slack messages silenced, but the associated issue is"
        " closed. Please remove them from the silenced_slack_notifications Airflow"
        " variable or assign a new issue."
    )
    for (dag, issue, predicate) in dags_to_reenable:
        message += f"\n  - <{issue}|{dag}: '{predicate}'>"
    send_alert(
        message, dag_id=DAG_ID, username="Silenced DAG Check", unfurl_links=False
    )
    return message


dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retry_delay": timedelta(minutes=1),
    },
    start_date=datetime(2022, 7, 29),
    schedule="@weekly",
    max_active_runs=MAX_ACTIVE,
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    tags=["maintenance"],
)

with dag:
    PythonOperator(
        task_id="check_silenced_dags_configuration",
        python_callable=check_configuration,
        op_kwargs={
            "github_pat": "{{ var.value.get('GITHUB_API_KEY', 'not_set') }}",
        },
    )
