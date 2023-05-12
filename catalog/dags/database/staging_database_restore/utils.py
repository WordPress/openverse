import functools

from airflow.providers.amazon.aws.hooks.rds import RdsHook

from database.staging_database_restore.constants import AWS_RDS_CONN_ID


def setup_rds_hook(func: callable) -> callable:
    """
    Provide an rds_hook as one of the parameters for the called function
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        rds_hook = RdsHook(aws_conn_id=AWS_RDS_CONN_ID)
        return func(*args, **kwargs, rds_hook=rds_hook)

    return wrapped
