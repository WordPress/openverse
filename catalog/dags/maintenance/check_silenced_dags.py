"""
# Silenced DAGs check

Check for DAGs that have silenced Slack alerts or skipped errors which may need to be
turned back on.

When a DAG has known failures, it can be omitted from Slack error reporting by adding
an entry to the `SILENCED_SLACK_NOTIFICATIONS` Airflow variable. Similarly, errors that
occur during the `pull_data` step may be configured to skip and allow ingestion to
continue, using the `SKIPPED_INGESTION_ERRORS` Airflow variable. These variables are
dictionaries where the key is the `dag_id` of the affected DAG, and the value is a list
of configuration dictionaries mapping an error `predicate` to be skipped/silenced to an
open GitHub issue.

The `check_silenced_dags` DAG iterates over the entries in the
`SILENCED_SLACK_NOTIFICATIONS` and `SKIPPED_INGESTION_ERRORS` configurations and
verifies that the associated GitHub issues are still open. If an issue has been closed,
it is assumed that the entry should be removed, and an alert is sent to prompt manual
update of the configuration. This prevents developers from forgetting to re-enable Slack
reporting or turnoff error skipping after the issue has been resolved.

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
from providers.provider_api_scripts.provider_data_ingester import SkippedIngestionError


logger = logging.getLogger(__name__)


DAG_ID = "check_silenced_dags"
MAX_ACTIVE = 1
CONFIGURATIONS = ["SILENCED_SLACK_NOTIFICATIONS", "SKIPPED_INGESTION_ERRORS"]


def get_issue_info(issue_url: str) -> tuple[str, str, str]:
    """Parse out the owner, repo, and issue_number from a GitHub issue url."""
    url_split = issue_url.split("/")
    if len(url_split) < 4:
        raise AirflowException(f"Issue url {issue_url} could not be parsed.")
    return url_split[-4], url_split[-3], url_split[-1]


def get_dags_with_closed_issues(
    github_pat: str,
    silenced_dags: dict[str, list[SilencedSlackNotification | SkippedIngestionError]],
) -> list[tuple[str, str, str, str | None]]:
    gh = GitHubAPI(github_pat)

    dags_to_reenable = []
    for dag_id, silenced_notifications in silenced_dags.items():
        for notification in silenced_notifications:
            issue_url = notification["issue"]
            owner, repo, issue_number = get_issue_info(issue_url)
            github_issue = gh.get_issue(repo, issue_number, owner)

            if github_issue.get("state") == "closed":
                # If the associated issue has been closed, this DAG can have
                # alerting re-enabled for this predicate.
                dags_to_reenable.append(
                    (
                        dag_id,
                        issue_url,
                        notification["predicate"],
                        notification.get("task_id_pattern"),
                    )
                )
    return dags_to_reenable


def check_configuration(github_pat: str, airflow_variable: str):
    configuration = Variable.get(
        airflow_variable, default_var={}, deserialize_json=True
    )

    dags_to_reenable = get_dags_with_closed_issues(github_pat, configuration)

    if not dags_to_reenable:
        raise AirflowSkipException(
            f"No configuration updates to {airflow_variable} needed."
        )

    message = (
        "The following DAG configurations are associated to a closed GitHub issue."
        f" Please remove them from the {airflow_variable} Airflow variable or assign"
        " a new issue."
    )

    for dag, issue, predicate, task_id_pattern in dags_to_reenable:
        dag_name = f"{dag} ({task_id_pattern})" if task_id_pattern else dag
        message += f"\n  - <{issue}|{dag_name}: '{predicate}'>"

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
    for airflow_variable in CONFIGURATIONS:
        PythonOperator(
            task_id=f"check_{airflow_variable.lower()}",
            python_callable=check_configuration,
            op_kwargs={
                "github_pat": "{{ var.value.get('GITHUB_API_KEY', 'not_set') }}",
                "airflow_variable": airflow_variable,
            },
        )
