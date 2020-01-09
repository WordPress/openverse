from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
from pytz import timezone
import os

airflowHome = os.environ['AIRFLOW_HOME']

args = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    #'email': 'data-engineer@creativecommons.org', #not configured
    #'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(days=1),
}


dag       = DAG(dag_id='Monthly_Workflow', default_args=args, schedule_interval='0 16 15 * *', catchup=False)#@monthly - the 15th at 16:00

beginTask = BashOperator(task_id='Begin_Monthly_Tasks', bash_command='echo Begin monthly tasks', dag=dag)

#reprocess Cleveland Museum's collection
cmaTask   = BashOperator(task_id='ClevelandMuseum',
                bash_command='python {0}/dags/api/ClevelandMuseum.py'.format(airflowHome),
                dag=dag)

#schedule the flickr task to reprocess data from the previous month
curMonth    = datetime.now().replace(day=1)
prevMonth   = curMonth - timedelta(days=1)
flickrTask  = BashOperator(task_id='Flickr_Monthly',
                bash_command='python {0}/dags/api/Flickr.py --month {1}'.format(airflowHome, prevMonth.strftime('%Y-%m')),
                dag=dag)

#sync the common crawl  AWS ETL data to the OUTPUT_DIR
s3SyncTask = BashOperator(task_id='Sync_Common_Crawl_Image_Data',
                bash_command='python {0}/dags/commoncrawl_s3_syncer/SyncImageProviders.py'.format(airflowHome),
                dag=dag)

#reprocess Rawpixel
rawpixelTask = BashOperator(task_id='RawPixel',
                bash_command='python {0}/dags/api/RawPixel.py'.format(airflowHome),
                dag=dag)

endTask      = BashOperator(task_id='End', trigger_rule=TriggerRule.ALL_DONE, bash_command='echo Terminating monthly workflow', dag=dag)

beginTask >> [cmaTask, rawpixelTask, flickrTask, s3SyncTask] >> endTask
