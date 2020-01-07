# TODO Decommission this file after testing the new separate DAGs.
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

def getTask(ds, **kwargs):
    print('Initializing API workflow')

    curTime = datetime.now().replace(microsecond=0,second=0,minute=0)
    curTime = curTime.astimezone(timezone('US/Eastern')).strftime("%H:%M")

    kwargs['ti'].xcom_push(key='task_exec_time', value=curTime)


def branchTask(**kwargs):
    curTime  = kwargs['ti'].xcom_pull(task_ids='Begin', key='task_exec_time')
    taskID   = schedTasks.get(curTime, None)

    return taskID

#TODO: Use airflow scheduled timestamp as the default date in the API scripts, instead of the system time, so that airflow can backfill any missing dag run instances.
schedTasks = {
    #'@hourly': 'Flickr'
    '07:00': 'Thingiverse',
    '09:00': 'MetMuseum',
    '11:00': 'PhyloPic',
    '13:00': 'WikimediaCommons'
    #'@monthly': 'ClevelandMuseum',
}


args = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    #'email': 'data-engineer@creativecommons.org', #not configured
    #'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
}

dag        = DAG(dag_id='Daily_ETL_Workflow', default_args=args, schedule_interval='0 * * * *', catchup=False)
beginTask  = PythonOperator(task_id='Begin', python_callable=getTask, provide_context=True, dag=dag)
forkTask   = BranchPythonOperator(task_id='Branch', python_callable=branchTask, provide_context=True, dag=dag)
hourlyTask = DummyOperator(task_id='HourlyTasks', dag=dag)

metTask    = BashOperator(task_id='MetMuseum',
                bash_command='python {0}/dags/api/MetMuseum.py --mode default'.format(airflowHome),
                dag=dag)

tvTask     = BashOperator(task_id='Thingiverse',
                bash_command='python {0}/dags/api/Thingiverse.py --mode default'.format(airflowHome),
                dag=dag)

ppTask     = BashOperator(task_id='PhyloPic',
                bash_command='python {0}/dags/api/PhyloPic.py --mode default'.format(airflowHome),
                dag=dag)

flickrTask  = BashOperator(task_id='Flickr',
                bash_command='python {0}/dags/api/Flickr.py --mode default'.format(airflowHome),
                priority_weight=7,
                dag=dag)

wmcTask     = BashOperator(task_id='WikimediaCommons',
                bash_command='python {0}/dags/api/WikimediaCommons.py --mode default'.format(airflowHome),
                dag=dag)

endTask    = BashOperator(task_id='End', trigger_rule=TriggerRule.ALL_DONE, bash_command='echo Terminating API workflows', dag=dag)

beginTask >> hourlyTask >> [flickrTask] >> endTask #schedule the flickr task to run hourly
beginTask >> forkTask >> [metTask, tvTask, ppTask, wmcTask] >> endTask #schedule the other API tasks to run based on the schdeuled time.
