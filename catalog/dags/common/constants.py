import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from common import slack


AUDIO = "audio"
IMAGE = "image"
MEDIA_TYPES = [AUDIO, IMAGE]
# The resource slugs used in API endpoints is not necessarily identical to the
# media type (for example, pluralized 'image' is 'images)
MEDIA_RESOURCE_SLUGS = {AUDIO: "audio", IMAGE: "images"}

MediaType = Literal["audio", "image"]

STAGING = "staging"
PRODUCTION = "production"

Environment = Literal["staging", "production"]
ENVIRONMENTS = [STAGING, PRODUCTION]

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2019, 1, 15),
    # Failure emails are on by default but the Slack failure callback will be used in
    # place of them if the DAG default args are used.
    "email_on_failure": False,
    "email_on_retry": False,
    "email": [CONTACT_EMAIL],
    "retries": int(os.getenv("DEFAULT_RETRY_COUNT", 2)),
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
    "on_failure_callback": slack.on_failure_callback,
}
XCOM_PULL_TEMPLATE = "{{{{ ti.xcom_pull(task_ids='{}', key='{}') }}}}"

POSTGRES_CONN_ID = "postgres_openledger_upstream"
OPENLEDGER_API_CONN_ID = "postgres_openledger_api"
POSTGRES_API_STAGING_CONN_ID = "postgres_openledger_api_staging"
AWS_CONN_ID = "aws_default"
AWS_CLOUDWATCH_CONN_ID = os.environ.get("AWS_CLOUDWATCH_CONN_ID", AWS_CONN_ID)
AWS_RDS_CONN_ID = os.environ.get("AWS_RDS_CONN_ID", AWS_CONN_ID)
ES_PROD_HTTP_CONN_ID = "elasticsearch_http_production"
API_HTTP_CONN_ID = "api_http"
REFRESH_POKE_INTERVAL = int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30))


@dataclass
class SQLInfo:
    """
    Configuration object for a media type's popularity SQL info.

    Required Constructor Arguments:

    media_table:                name of the main media table
    metrics_table:              name of the popularity metrics table
    standardized_popularity_fn: name of the standardized_popularity sql
                                function
    popularity_percentile_fn:   name of the popularity percentile sql
                                function

    """

    media_table: str
    metrics_table: str
    standardized_popularity_fn: str
    popularity_percentile_fn: str


SQL_INFO_BY_MEDIA_TYPE = {
    AUDIO: SQLInfo(
        media_table=AUDIO,
        metrics_table="audio_popularity_metrics",
        standardized_popularity_fn="standardized_audio_popularity",
        popularity_percentile_fn="audio_popularity_percentile",
    ),
    IMAGE: SQLInfo(
        media_table=IMAGE,
        metrics_table="image_popularity_metrics",
        standardized_popularity_fn="standardized_image_popularity",
        popularity_percentile_fn="image_popularity_percentile",
    ),
}
