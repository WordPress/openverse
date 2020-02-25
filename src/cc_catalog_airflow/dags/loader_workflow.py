from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
# from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import os

DB_NAME = 'postgres_openledger_upstream'


def verify_loading_table():
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


def load_data():
    tsv_file_name = get_oldest_file(5)
    if tsv_file_name is not None:
        import_data_to_intermediate_table(tsv_file_name)
        upsert_records_to_image_table()
        delete_old_records_and_file(tsv_file_name)


def get_oldest_file(minimum_age_minutes):
    oldest_file_name = None
    output_dir = os.environ['OUTPUT_DIR']
    print(f'getting files from {output_dir}')
    path_list = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f[-4:] == '.tsv'
    ]
    print(f'found files:\n{path_list}')
    path_last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    print(f'last_modified_list:\n{path_list}')
    oldest_file_modified = min(path_last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        print(f'no file found older than {minimum_age_minutes} minutes.')

    return oldest_file_name


def import_data_to_intermediate_table(tsv_file_name):
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


def upsert_records_to_image_table():
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


def delete_old_records_and_file(tsv_file_name):
    postgres = PostgresHook(postgres_conn_id=DB_NAME)
    postgres.run('DELETE FROM provider_image_data;')
    os.remove(tsv_file_name)


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

begin_task = BashOperator(
    task_id='Begin',
    dag=dag,
    bash_command='echo Begin DB Loader'
)

end_task = BashOperator(
    task_id='End',
    dag=dag,
    bash_command='echo Terminating DB Loader'
)

verify_task = PythonOperator(
    task_id='Verify',
    provide_context=False,
    python_callable=verify_loading_table,
    dag=dag
)

load_task = PythonOperator(
    task_id='Load',
    provide_context=False,
    python_callable=load_data,
    dag=dag
)

begin_task >> verify_task >> load_task >> end_task
