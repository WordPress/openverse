import logging
from typing import Tuple

from airflow.exceptions import AirflowException, AirflowSkipException
from airflow.models import Variable
from common.github import GitHubAPI
from common.slack import send_alert


logger = logging.getLogger(__name__)


def get_issue_info(issue_url: str) -> Tuple[str, str, str]:
    """
    Parses out the owner, repo, and issue_number from a GitHub issue url.
    """
    url_split = issue_url.split("/")
    if len(url_split) < 4:
        raise AirflowException(f"Issue url {issue_url} could not be parsed.")
    return url_split[-4], url_split[-3], url_split[-1]


def get_dags_with_closed_issues(github_pat, silenced_dags):
    gh = GitHubAPI(github_pat)

    dags_to_reenable = []
    for dag_id, issue_url in silenced_dags.items():
        owner, repo, issue_number = get_issue_info(issue_url)
        github_issue = gh.get_issue(repo, issue_number, owner)

        if github_issue.get("state") == "closed":
            # If the associated issue has been closed, this DAG can have
            # alerting reenabled.
            dags_to_reenable.append((dag_id, issue_url))
    return dags_to_reenable


def check_configuration(github_pat: str, airflow_variable: str):
    silenced_dags = Variable.get(airflow_variable, {}, deserialize_json=True)
    dags_to_reenable = get_dags_with_closed_issues(github_pat, silenced_dags)

    if not dags_to_reenable:
        raise AirflowSkipException(
            "All DAGs configured to silence messages have work still in progress."
            " No configuration updates needed."
        )

    message = (
        "The following DAGs have Slack messages silenced, but the associated issue is"
        f" closed. Please remove them from the `{airflow_variable}` Airflow variable"
        " or assign a new issue."
    )
    for (dag, issue) in dags_to_reenable:
        message += f"\n  - <{issue}|{dag}>"
    send_alert(message, username="Silenced DAG Check", unfurl_links=False)
    return message
