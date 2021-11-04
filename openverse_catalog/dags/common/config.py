import os
from datetime import datetime, timedelta


CRONTAB_STR = "crontab_str"
SCRIPT = "script"

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2019, 1, 15),
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
}

# The DAG_VARIABLES dict holds variables that differentiate the dags
# between API sources. The entry for each source should have the
# following format:
#   <source>: {
#       'script': os.path.join(api_script_path, <source_script>),
#       'crontab_str': <some_crontab_string>,
#   }
# The `crontab_str` key is optional, and should be either a
# crontab-style string specifying when the particular script should
# be run, or a shorthand known to airflow (see
# https://airflow.apache.org/docs/stable/scheduler.html). Omitting that
# key results in a DAG that runs only when the user clicks 'play' in the
# airflow interface.

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")
API_SCRIPT_PATH = os.path.join(AIRFLOW_HOME, "dags", "provider_api_scripts")


DAG_VARIABLES = {
    "thingiverse": {
        SCRIPT: os.path.join(API_SCRIPT_PATH, "Thingiverse.py"),
        CRONTAB_STR: "0 7 * * *",
    },
}
