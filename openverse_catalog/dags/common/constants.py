from datetime import datetime, timedelta

from common import slack


AUDIO = "audio"
IMAGE = "image"
MEDIA_TYPES = [AUDIO, IMAGE]

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2019, 1, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
    "on_failure_callback": slack.on_failure_callback,
}
XCOM_PULL_TEMPLATE = "{{{{ ti.xcom_pull(task_ids='{}', key='{}') }}}}"
