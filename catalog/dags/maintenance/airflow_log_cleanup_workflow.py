"""
# Clean up airflow logs

A maintenance workflow that you can deploy into Airflow to periodically clean
out the task logs to avoid those getting too big. By default, this will also
clean child process logs from the 'scheduler' directory.

Can remove all log files by setting "maxLogAgeInDays" to -1.
If you want to test the DAG in the Airflow Web UI, you can also set
enableDelete to `false`, and then you will see a list of log folders
that can be deleted, but will not actually delete them.

This should all go on one line:
```
airflow dags trigger --conf
'{"maxLogAgeInDays":-1, "enableDelete": "false"}' airflow_log_cleanup
```
`--conf` options:
- maxLogAgeInDays:<INT> - Optional
- enableDelete:<BOOLEAN> - Optional
"""

from datetime import datetime, timedelta

import jinja2
from airflow.configuration import conf
from airflow.models import DAG
from airflow.operators.python import PythonOperator

from common import log_cleanup
from common.constants import DAG_DEFAULT_ARGS


DAG_ID = "airflow_log_cleanup"
BASE_LOG_FOLDER = conf.get("logging", "BASE_LOG_FOLDER").rstrip("/")
# Whether the job should delete the logs or not. Included if you want to
# temporarily avoid deleting the logs
DEFAULT_MAX_LOG_AGE_IN_DAYS = 7
ENABLE_DELETE = True
MAX_ACTIVE_TASKS = 1
# should we send someone an email when this DAG fails?
ALERT_EMAIL_ADDRESSES = ""

dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retry_delay": timedelta(minutes=1),
        "template_undefined": jinja2.Undefined,
    },
    start_date=datetime(2020, 6, 15),
    schedule="@weekly",
    max_active_tasks=MAX_ACTIVE_TASKS,
    max_active_runs=MAX_ACTIVE_TASKS,
    # If this was True, airflow would run this DAG in the beginning
    # for each day from the start day to now
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    tags=["maintenance"],
)

with dag:
    PythonOperator(
        task_id="log_cleaner_operator",
        python_callable=log_cleanup.clean_up,
        op_args=[
            BASE_LOG_FOLDER,
            "{{ params.get('maxLogAgeInDays') }}",
            "{{ params.get('enableDelete') }}",
        ],
    )
