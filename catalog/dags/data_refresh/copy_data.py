import logging

from airflow.decorators import task

from common.constants import Environment, MediaType


logger = logging.getLogger(__name__)


@task
def copy_upstream_table(environment: Environment, media_type: MediaType):
    logger.info("Hello world")
    return
