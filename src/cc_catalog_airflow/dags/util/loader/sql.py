import logging
from airflow.hooks.postgres_hook import PostgresHook
from util.loader import column_names as col

logger = logging.getLogger(__name__)

LOAD_TABLE_NAME_STUB = 'provider_image_data'
IMAGE_TABLE_NAME = 'image'
DB_USER_NAME = 'deploy'
NOW = 'NOW()'
FALSE = "'f'"


def create_loading_table(
        postgres_conn_id,
        identifier
):
    """
    Create intermediary table and indices if they do not exist
    """
    load_table = _get_load_table_name(identifier)
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(
        f'CREATE TABLE public.{load_table} ('
        f'\n  {col.FOREIGN_IDENTIFIER} character varying(3000),'
        f'\n  {col.FOREIGN_LANDING_URL} character varying(1000),'
        f'\n  {col.DIRECT_URL} character varying(3000),'
        f'\n  {col.THUMBNAIL} character varying(3000),'
        f'\n  {col.WIDTH} integer,'
        f'\n  {col.HEIGHT} integer,'
        f'\n  {col.FILESIZE} character varying(100),'
        f'\n  {col.LICENSE} character varying(50),'
        f'\n  {col.LICENSE_VERSION} character varying(25),'
        f'\n  {col.CREATOR} character varying(2000),'
        f'\n  {col.CREATOR_URL} character varying(2000),'
        f'\n  {col.TITLE} character varying(5000),'
        f'\n  {col.META_DATA} jsonb,'
        f'\n  {col.TAGS} jsonb,'
        f'\n  {col.WATERMARKED} boolean,'
        f'\n  {col.PROVIDER} character varying(80),'
        f'\n  {col.SOURCE} character varying(80)'
        f'\n);'
    )
    postgres.run(
        f'ALTER TABLE public.{load_table} OWNER TO {DB_USER_NAME};'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_{col.PROVIDER}_key'
        f' ON public.{load_table} USING btree ({col.PROVIDER});'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_{col.FOREIGN_IDENTIFIER}_key'
        f' ON public.{load_table}'
        f' USING btree (provider, md5(({col.FOREIGN_IDENTIFIER})::text));'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_{col.DIRECT_URL}_key'
        f' ON public.{load_table}'
        f' USING btree (provider, md5(({col.DIRECT_URL})::text));'
    )


def load_local_data_to_intermediate_table(
        postgres_conn_id,
        tsv_file_name,
        identifier
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Loading {tsv_file_name} into {load_table}')

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.bulk_load(f'{load_table}', tsv_file_name)
    _clean_intermediate_table_data(postgres, load_table)


def load_s3_data_to_intermediate_table(
        postgres_conn_id,
        bucket,
        s3_key,
        identifier
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Loading {s3_key} from S3 Bucket {bucket} into {load_table}')

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(
        f"SELECT aws_s3.table_import_from_s3("
        f"'{load_table}',"
        f"'',"
        f"'DELIMITER E''\t''',"
        f"'{bucket}',"
        f"'{s3_key}',"
        f"'us-east-1'"
        f");"
    )
    _clean_intermediate_table_data(postgres, load_table)


def _clean_intermediate_table_data(
        postgres_hook,
        load_table
):
    postgres_hook.run(
        f'DELETE FROM {load_table} WHERE {col.DIRECT_URL} IS NULL;'
    )
    postgres_hook.run(
        f'DELETE FROM {load_table} WHERE {col.LICENSE} IS NULL;'
    )
    postgres_hook.run(
        f'DELETE FROM {load_table} WHERE {col.FOREIGN_LANDING_URL} IS NULL;'
    )
    postgres_hook.run(
        f'DELETE FROM {load_table} WHERE {col.FOREIGN_IDENTIFIER} IS NULL;'
    )
    postgres_hook.run(
        f'DELETE FROM {load_table} p1'
        f' USING {load_table} p2'
        f' WHERE p1.ctid < p2.ctid'
        f' AND p1.{col.PROVIDER} = p2.{col.PROVIDER}'
        f' AND p1.{col.FOREIGN_IDENTIFIER} = p2.{col.FOREIGN_IDENTIFIER};'
    )


def upsert_records_to_image_table(
        postgres_conn_id,
        identifier,
        image_table=IMAGE_TABLE_NAME
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Upserting new records into {image_table}.')
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    image_columns = [
            col.CREATED_ON,
            col.UPDATED_ON,
            col.PROVIDER,
            col.SOURCE,
            col.FOREIGN_IDENTIFIER,
            col.FOREIGN_LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.WIDTH,
            col.HEIGHT,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.LAST_SYNCED,
            col.REMOVED,
            col.META_DATA,
            col.TAGS,
            col.WATERMARKED
        ]
    insert_values = image_columns[:]
    insert_values[0], insert_values[1], insert_values[15] = NOW, NOW, NOW
    insert_values[16] = FALSE
    # print(insert_values)
    postgres.run(
        f'INSERT INTO {image_table} ('
        + ', '.join(image_columns)
        + ')\n'
        'SELECT '
        + ', '.join(insert_values)
        + f'\nFROM {load_table}\n'
        + 'ON CONFLICT ('
        + f'{col.PROVIDER}, '
        + f' md5(({col.FOREIGN_IDENTIFIER})::text),'
        + f'md5(({col.DIRECT_URL})::text))\n'
        + 'DO UPDATE SET '
        + f'\n  updated_on = {NOW}'
        + _newest_non_null('foreign_landing_url')
        + _newest_non_null('url')
        + _newest_non_null('thumbnail')
        + _newest_non_null('width')
        + _newest_non_null('height')
        + _newest_non_null('license')
        + _newest_non_null('license_version')
        + _newest_non_null('creator')
        + _newest_non_null('creator_url')
        + _newest_non_null('title')
        + f',\n  last_synced_with_source = {NOW}'
        + f',\n  removed_from_source = {FALSE}, '
        + "meta_data = EXCLUDED.meta_data"  # TODO
        + _newest_non_null('watermarked')
        + f'\nWHERE {image_table}.{col.FOREIGN_IDENTIFIER} '
        + f'= EXCLUDED.{col.FOREIGN_IDENTIFIER}'
        + f' AND {image_table}.{col.PROVIDER} = EXCLUDED.{col.PROVIDER};'
    )


def drop_load_table(postgres_conn_id, identifier):
    load_table = _get_load_table_name(identifier)
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f'DROP TABLE {load_table};')


def _get_load_table_name(
        identifier,
        load_table_name_stub=LOAD_TABLE_NAME_STUB,
):
    return f'{load_table_name_stub}{identifier}'


def _newest_non_null(column):
    return f',\n  {column} = EXCLUDED.{column}'
