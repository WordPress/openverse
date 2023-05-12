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


def ensure_staging(func: callable) -> callable:
    """
    Ensure that the staging database is the one being used for a target function.
    This requires that the target function has a db_instance parameter in its keyword
    arguments.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if "db_identifier" not in kwargs:
            raise ValueError("The target function must have a db_identifier parameter")
        db_identifier = kwargs["db_identifier"]
        if db_identifier != constants.STAGING_IDENTIFIER:
            raise ValueError(
                f"The target function must be called with the staging database "
                f"identifier ({constants.STAGING_IDENTIFIER}), not {db_identifier}"
            )
        return func(*args, **kwargs)

    return wrapped
