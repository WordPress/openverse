from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
from pytz import timezone
import os

DB_NAME = 'postgres_openledger_upstream'

def verifyTable():
    pgHook  = PostgresHook(postgres_conn_id=DB_NAME)

    query = """CREATE TABLE IF NOT EXISTS public.provider_image_data (
                    foreign_identifier character varying(3000),
                    foreign_landing_url character varying(1000),
                    url character varying(3000),
                    thumbnail character varying(3000),
                    width integer,
                    height integer,
                    filesize character varying(100),
                    license character varying(50),
                    license_version character varying(25),
                    creator character varying(2000),
                    creator_url character varying(2000),
                    title character varying(5000),
                    meta_data jsonb,
                    tags jsonb,
                    watermarked boolean,
                    provider character varying(80),
                    source character varying(80)
                );"""
    pgHook.run(query)

    query = 'ALTER TABLE public.provider_image_data OWNER TO deploy;'
    pgHook.run(query)

    #CREATE INDEX
    query = 'CREATE INDEX IF NOT EXISTS provider_image_data_provider_key ON public.provider_image_data USING btree (provider);'
    pgHook.run(query)

    query = 'CREATE INDEX IF NOT EXISTS provider_image_data_foreign_identifier_key ON public.provider_image_data USING btree (provider, md5((foreign_identifier)::text));'
    pgHook.run(query)

    query = 'CREATE INDEX IF NOT EXISTS provider_image_data_url_key ON public.provider_image_data USING btree (provider, md5((url)::text));'
    pgHook.run(query)


def loadData():
    #create intermediary table and indices if they do not exist
    verifyTable()

    #get all tsv files that are in the output directory
    tsvFiles = getTextFiles()
    if tsvFiles:
        tsvFiles = list(tsvFiles)
    else:
        return None
    print('Preparing to load the following file(s): {}'.format(','.join(tsvFiles)))

    #load each file into the DB
    #map(lambda fp: importData(fp), tsvFiles)
    for fp in tsvFiles:
        importData(fp)


def getTextFiles():
    outputDir   = os.environ['OUTPUT_DIR']
    fileList    = os.listdir(outputDir)
    curTime     = datetime.now()
    endTime     = curTime - timedelta(minutes=15)

    if fileList:
        #filter TSV files
        fileList = filter(lambda fp: fp.endswith('.tsv'), fileList)

        #get all files that were not modified in the last 15 minutes
        fileList = filter(lambda fp: datetime.fromtimestamp(
                                os.stat(os.path.join(outputDir, fp)).st_mtime) <= endTime,
                        fileList)

        if fileList:
            return map(lambda fp: '{}{}'.format(outputDir, fp), fileList)


def importData(_filename):
    print('Processing: {}'.format(_filename))

    pgHook  = PostgresHook(postgres_conn_id=DB_NAME)

    #LOAD the data INTO the intermediary table
    pgHook.bulk_load('provider_image_data', _filename)


    #DELETE invalid records
    pgHook.run('DELETE FROM provider_image_data WHERE url IS NULL;')
    pgHook.run('DELETE FROM provider_image_data WHERE license IS NULL;')
    pgHook.run('DELETE FROM provider_image_data WHERE foreign_landing_url IS NULL;')
    pgHook.run('DELETE FROM provider_image_data WHERE foreign_identifier IS NULL;')


    #DELETE duplicate records
    pgHook.run('DELETE FROM provider_image_data p1 USING provider_image_data p2 WHERE p1.ctid < p2.ctid and p1.provider = p2.provider and p1.foreign_identifier = p2.foreign_identifier;')


    #UPSERT the records
    query = """INSERT INTO image (created_on, updated_on, provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, width, height, license, license_version, creator, creator_url, title, last_synced_with_source, removed_from_source, meta_data, tags, watermarked)
        SELECT NOW(), NOW(), provider, source, foreign_identifier, foreign_landing_url, url, thumbnail, width, height, license, license_version, creator, creator_url, title, NOW(), 'f', meta_data, tags, watermarked
        FROM provider_image_data
        ON CONFLICT (provider, md5((foreign_identifier)::text), md5((url)::text))
        DO UPDATE SET updated_on = now(), foreign_landing_url = EXCLUDED.foreign_landing_url, url = EXCLUDED.url, thumbnail = EXCLUDED.thumbnail, width = EXCLUDED.width, height = EXCLUDED.height, license = EXCLUDED.license, license_version = EXCLUDED.license_version, creator = EXCLUDED.creator, creator_url = EXCLUDED.creator_url, title = EXCLUDED.title, last_synced_with_source = NOW(), removed_from_source = 'f', meta_data = EXCLUDED.meta_data, watermarked = EXCLUDED.watermarked
        WHERE image.foreign_identifier = EXCLUDED.foreign_identifier and image.provider = EXCLUDED.provider;"""

    pgHook.run(query)


    #delete rows from the intermediary table
    #If the above task was NOT successful, the task state will switch to 'up for retry' and the tasks below will not be performed (i.e. it will be queued until its preceding task is successful
    pgHook.run('DELETE FROM provider_image_data;')

    #REMOVE the file that was loaded
    os.remove(_filename) if os.path.exists(_filename) else None


args = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    #'email': 'data-engineer@creativecommons.org', #not configured
    #'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=30),
}

dag       = DAG(dag_id='DB_Loader', default_args=args, schedule_interval='0 */4 * * *', catchup=False) #run every 4 hours

beginTask = BashOperator(task_id='Begin', dag=dag, bash_command='echo Begin DB Loader')

endTask   = BashOperator(task_id='End', dag=dag, bash_command='echo Terminating DB Loader')

loadTask  = PythonOperator(task_id='Load', provide_context=False, python_callable=loadData, dag=dag)

beginTask >> loadTask >> endTask
