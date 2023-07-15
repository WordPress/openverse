import functools

from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.rds import RdsHook

from common.constants import AWS_RDS_CONN_ID
from common.github import GitHubAPI
from database.staging_database_restore import constants


def setup_rds_hook(func: callable) -> callable:
    """
    Provide an rds_hook as one of the parameters for the called function.
    If the function is explicitly supplied with an rds_hook, use that one.
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        rds_hook = kwargs.pop("rds_hook", None) or RdsHook(aws_conn_id=AWS_RDS_CONN_ID)
        return func(*args, **kwargs, rds_hook=rds_hook)

    return wrapped


def setup_github(func: callable) -> callable:
    """
    Provide an instance of the GitHubAPI as one of the parameters for the
    called function. If the function is explicitly supplied with a github instance,
    use that one.
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        github_pat = Variable.get("GITHUB_API_KEY")
        github = kwargs.pop("github", None) or GitHubAPI(github_pat)
        return func(*args, **kwargs, github=github)

    return wrapped


def ensure_mutate_allowed(db_identifier: str) -> None:
    """
    Ensure that the only those databases which are safe to mutate are being used
    for a target function.
    """

    if db_identifier not in constants.SAFE_TO_MUTATE:
        raise ValueError(
            f"The target function must be called with a non-production database "
            f"identifier, not {db_identifier}"
        )
