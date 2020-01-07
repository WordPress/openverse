from datetime import datetime, timedelta
import os

dag_default_args = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    #'email': 'data-engineer@creativecommons.org', #not configured
    #'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
}

airflow_home = os.getenv('AIRFLOW_HOME')
print(airflow_home)
api_script_path = os.path.join(airflow_home, 'dags/provider_api_scripts')

# The dag_variables dict holds variables that differentiate the dags
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
dag_variables = {
    'flickr': {
        'script': os.path.join(api_script_path, 'Flickr.py'),
    },
    'met_museum': {
        'script': os.path.join(api_script_path, 'MetMuseum.py'),
    },
    'phylo_pic': {
        'script': os.path.join(api_script_path, 'PhyloPic.py'),
    },
    'thingiverse': {
        'script': os.path.join(api_script_path, 'Thingiverse.py'),
    },
    'wikimedia_commons': {
        'script': os.path.join(api_script_path, 'WikimediaCommons.py'),
        'crontab_str': '0 13 * * *'
    },
}
