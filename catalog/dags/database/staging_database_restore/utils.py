import functools

from airflow.providers.amazon.aws.hooks.rds import RdsHook

from database.staging_database_restore import constants


def setup_rds_hook(func: callable) -> callable:
    """
    Provide an rds_hook as one of the parameters for the called function
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        rds_hook = RdsHook(aws_conn_id=constants.AWS_RDS_CONN_ID)
        return func(*args, **kwargs, rds_hook=rds_hook)

    return wrapped


def ensure_staging(db_identifier: str) -> None:
    """
    Ensure that the staging database is the one being used for a target function.
    This requires that the target function has a db_instance parameter in its keyword
    arguments.
    """

    if db_identifier not in constants.SAFE_TO_MUTATE:
        raise ValueError(
            f"The target function must be called with the staging database "
            f"identifier ({constants.STAGING_IDENTIFIER}), not {db_identifier}"
        )
