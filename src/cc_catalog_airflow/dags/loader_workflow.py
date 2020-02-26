from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import ShortCircuitOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import os

DB_NAME = 'postgres_openledger_upstream'
FILE_CHANGE_WAIT = 5
FAILURE_DIRECTORY = 'failures'


def _create_if_not_exists_loading_table():
    """
    Create intermediary table and indices if they do not exist
    """
    postgres = PostgresHook(postgres_conn_id=DB_NAME)
    postgres.run(
        'CREATE TABLE IF NOT EXISTS public.provider_image_data ('
        'foreign_identifier character varying(3000), '
        'foreign_landing_url character varying(1000), '
        'url character varying(3000), '
        'thumbnail character varying(3000), '
        'width integer, '
        'height integer, '
        'filesize character varying(100), '
        'license character varying(50), '
        'license_version character varying(25), '
        'creator character varying(2000), '
        'creator_url character varying(2000), '
        'title character varying(5000), '
        'meta_data jsonb, '
        'tags jsonb, '
        'watermarked boolean, '
        'provider character varying(80), '
        'source character varying(80)'
        ');'
    )
    postgres.run(
        'ALTER TABLE public.provider_image_data OWNER TO deploy;'
    )
    postgres.run(
        'CREATE INDEX IF NOT EXISTS provider_image_data_provider_key'
        ' ON public.provider_image_data USING btree (provider);'
    )
    postgres.run(
        'CREATE INDEX IF NOT EXISTS provider_image_data_foreign_identifier_key'
        ' ON public.provider_image_data'
        ' USING btree (provider, md5((foreign_identifier)::text));'
    )
    postgres.run(
        'CREATE INDEX IF NOT EXISTS provider_image_data_url_key'
        ' ON public.provider_image_data'
        ' USING btree (provider, md5((url)::text));'
    )


def _load_data():
    tsv_file_name = _get_oldest_file()
    _import_data_to_intermediate_table(tsv_file_name)
    _upsert_records_to_image_table()


def _get_oldest_file(minimum_age_minutes=FILE_CHANGE_WAIT):
    oldest_file_name = None
    output_dir = os.environ['OUTPUT_DIR']
    print(f'getting files from {output_dir}')
    path_list = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f[-4:] == '.tsv'
    ]
    print(f'found files:\n{path_list}')
    last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    print(f'last_modified_list:\n{last_modified_list}')

    if not last_modified_list:
        return

    oldest_file_modified = min(last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        print(f'no file found older than {minimum_age_minutes} minutes.')

    return oldest_file_name


def _import_data_to_intermediate_table(tsv_file_name):
    print(f'Loading {tsv_file_name} into intermediate table')

    postgres = PostgresHook(postgres_conn_id=DB_NAME)
    postgres.bulk_load('provider_image_data', tsv_file_name)
    postgres.run(
        'DELETE FROM provider_image_data WHERE url IS NULL;'
    )
    postgres.run(
        'DELETE FROM provider_image_data WHERE license IS NULL;'
    )
    postgres.run(
        'DELETE FROM provider_image_data WHERE foreign_landing_url IS NULL;'
    )
    postgres.run(
        'DELETE FROM provider_image_data WHERE foreign_identifier IS NULL;'
    )
    postgres.run(
        'DELETE FROM provider_image_data p1'
        ' USING provider_image_data p2'
        ' WHERE p1.ctid < p2.ctid'
        ' AND p1.provider = p2.provider'
        ' AND p1.foreign_identifier = p2.foreign_identifier;'
    )


def _upsert_records_to_image_table():
    print('Upserting new records into image table.')
    postgres = PostgresHook(postgres_conn_id=DB_NAME)
    postgres.run(
        "INSERT INTO image ("
        "created_on, updated_on, provider, source, foreign_identifier, "
        "foreign_landing_url, url, thumbnail, width, height, license, "
        "license_version, creator, creator_url, title, "
        "last_synced_with_source, removed_from_source, meta_data, tags, "
        "watermarked)\n"
        "SELECT NOW(), NOW(), provider, source, foreign_identifier, "
        "foreign_landing_url, url, thumbnail, width, height, license, "
        "license_version, creator, creator_url, title, NOW(), 'f', "
        "meta_data, tags, watermarked\n"
        "FROM provider_image_data\n"
        "ON CONFLICT ("
        "provider, md5((foreign_identifier)::text), md5((url)::text)"
        ")\n"
        "DO UPDATE SET "
        "updated_on = NOW(), "
        "foreign_landing_url = EXCLUDED.foreign_landing_url, "
        "url = EXCLUDED.url, "
        "thumbnail = EXCLUDED.thumbnail, "
        "width = EXCLUDED.width, "
        "height = EXCLUDED.height, "
        "license = EXCLUDED.license, "
        "license_version = EXCLUDED.license_version, "
        "creator = EXCLUDED.creator, "
        "creator_url = EXCLUDED.creator_url, "
        "title = EXCLUDED.title, "
        "last_synced_with_source = NOW(), "
        "removed_from_source = 'f', "
        "meta_data = EXCLUDED.meta_data, "
        "watermarked = EXCLUDED.watermarked\n"
        "WHERE image.foreign_identifier = EXCLUDED.foreign_identifier"
        " AND image.provider = EXCLUDED.provider;"
    )


def _delete_old_records_and_file():
    postgres = PostgresHook(postgres_conn_id=DB_NAME)
    tsv_file_name = _get_oldest_file()
    postgres.run('DELETE FROM provider_image_data;')
    print(f'Deleting {tsv_file_name}')
    os.remove(tsv_file_name)


def _create_if_not_exists_failure_directory():
    output_dir = os.environ['OUTPUT_DIR']
    if not os.path.exists(os.path.join(output_dir, FAILURE_DIRECTORY)):
        os.mkdir(os.path.join(output_dir, FAILURE_DIRECTORY))


def _move_failure():
    output_dir = os.environ['OUTPUT_DIR']
    tsv_file_name = _get_oldest_file(),
    os.rename(
        tsv_file_name,
        os.path.join(
            output_dir,
            FAILURE_DIRECTORY,
            os.path.basename(tsv_file_name)
        )
    )
    if not os.path.exists(os.path.join(output_dir, FAILURE_DIRECTORY)):
        os.mkdir(os.path.join(output_dir, FAILURE_DIRECTORY))


args = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15),
}

dag = DAG(
    dag_id='new_DB_Loader',
    default_args=args,
    concurrency=1,
    max_active_runs=1,
    schedule_interval='* * * * *',
    catchup=False
)

check_for_oldest_file = ShortCircuitOperator(
    task_id='check_for_oldest_file',
    python_callable=_get_oldest_file,
    dag=dag
)

create_table = PythonOperator(
    task_id='create_table',
    python_callable=_create_if_not_exists_loading_table,
    dag=dag
)

load_data = PythonOperator(
    task_id='load_data',
    python_callable=_load_data,
    dag=dag
)

delete_file = PythonOperator(
    task_id='delete_file',
    python_callable=_delete_old_records_and_file,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)

create_failure_directory = PythonOperator(
    task_id='create_failure_directory_task',
    python_callable=_create_if_not_exists_failure_directory,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

move_failure = PythonOperator(
    task_id='move_failure',
    python_callable=_move_failure,
    dag=dag
)

(
    check_for_oldest_file
    >> create_table
    >> load_data
    >> [delete_file, create_failure_directory]
)
create_failure_directory >> move_failure
