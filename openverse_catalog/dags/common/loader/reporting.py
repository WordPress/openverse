import logging

from common.slack import send_message


logger = logging.getLogger(__name__)


def report_completion(provider_name, media_type, duration, record_count):
    """
    Send a Slack notification when the load_data task has completed.
    Messages are only sent out in production and if a Slack connection is defined.
    In all cases the data is logged.
    """

    # This happens when the task is manually set to `success` in Airflow before
    # completing.
    duration = "_No data_" if duration == "None" else duration

    message = f"""
*Provider*: `{provider_name}`
*Media Type*: `{media_type}`
*Number of Records Upserted*: {record_count}
*Duration of data pull task*: {duration}

* _Duration includes time taken to pull data of all media types._
"""
    send_message(message, username="Airflow DAG Load Data Complete")
    logger.info(message)
