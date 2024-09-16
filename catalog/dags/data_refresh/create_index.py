"""
# Create Index

This file contains TaskGroups related to creating Elasticsearch indices
as part of the Data Refresh.
"""

import logging
import uuid

from airflow.decorators import task, task_group

from common import elasticsearch as es
from data_refresh.data_refresh_types import DataRefreshConfig
from data_refresh.es_mapping import index_settings


logger = logging.getLogger(__name__)


@task
def generate_index_name(media_type: str) -> str:
    return f"{media_type}-{uuid.uuid4().hex}"


@task_group(group_id="create_temp_index")
def create_index(
    data_refresh_config: DataRefreshConfig,
    es_host: str,
):
    # Generate a UUID suffix that will be used by the newly created index.
    temp_index_name = generate_index_name(media_type=data_refresh_config.media_type)

    # Create a new index
    es.create_index(
        index_config={
            "index": temp_index_name,
            "body": index_settings(data_refresh_config.media_type),
        },
        es_host=es_host,
    )

    # Return the name of the created index
    return temp_index_name
