import logging
from airflow.hooks.postgres_hook import PostgresHook

logger = logging.getLogger(__name__)

LOAD_TABLE_NAME_STUB = 'provider_image_data'
IMAGE_TABLE_NAME = 'image'


def create_if_not_exists_loading_table(
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
        f'foreign_identifier character varying(3000), '
        f'foreign_landing_url character varying(1000), '
        f'url character varying(3000), '
        f'thumbnail character varying(3000), '
        f'width integer, '
        f'height integer, '
        f'filesize character varying(100), '
        f'license character varying(50), '
        f'license_version character varying(25), '
        f'creator character varying(2000), '
        f'creator_url character varying(2000), '
        f'title character varying(5000), '
        f'meta_data jsonb, '
        f'tags jsonb, '
        f'watermarked boolean, '
        f'provider character varying(80), '
        f'source character varying(80)'
        f');'
    )
    postgres.run(
        f'ALTER TABLE public.{load_table} OWNER TO deploy;'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_provider_key'
        f' ON public.{load_table} USING btree (provider);'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_foreign_identifier_key'
        f' ON public.{load_table}'
        f' USING btree (provider, md5((foreign_identifier)::text));'
    )
    postgres.run(
        f'CREATE INDEX IF NOT EXISTS {load_table}_url_key'
        f' ON public.{load_table}'
        f' USING btree (provider, md5((url)::text));'
    )


def import_data_to_intermediate_table(
        postgres_conn_id,
        tsv_file_name,
        identifier
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Loading {tsv_file_name} into {load_table}')

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.bulk_load(f'{load_table}', tsv_file_name)
    postgres.run(
        f'DELETE FROM {load_table} WHERE url IS NULL;'
    )
    postgres.run(
        f'DELETE FROM {load_table} WHERE license IS NULL;'
    )
    postgres.run(
        f'DELETE FROM {load_table} WHERE foreign_landing_url IS NULL;'
    )
    postgres.run(
        f'DELETE FROM {load_table} WHERE foreign_identifier IS NULL;'
    )
    postgres.run(
        f'DELETE FROM {load_table} p1'
        f' USING {load_table} p2'
        f' WHERE p1.ctid < p2.ctid'
        f' AND p1.provider = p2.provider'
        f' AND p1.foreign_identifier = p2.foreign_identifier;'
    )


def upsert_records_to_image_table(
        postgres_conn_id,
        identifier,
        image_table=IMAGE_TABLE_NAME
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Upserting new records into {image_table}.')
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(
        f"INSERT INTO {image_table} ("
        f"created_on, updated_on, provider, source, foreign_identifier, "
        f"foreign_landing_url, url, thumbnail, width, height, license, "
        f"license_version, creator, creator_url, title, "
        f"last_synced_with_source, removed_from_source, meta_data, tags, "
        f"watermarked)\n"
        f"SELECT NOW(), NOW(), provider, source, foreign_identifier, "
        f"foreign_landing_url, url, thumbnail, width, height, license, "
        f"license_version, creator, creator_url, title, NOW(), 'f', "
        f"meta_data, tags, watermarked\n"
        f"FROM {load_table}\n"
        f"ON CONFLICT ("
        f"provider, md5((foreign_identifier)::text), md5((url)::text)"
        f")\n"
        f"DO UPDATE SET "
        f"updated_on = NOW(), "
        f"foreign_landing_url = EXCLUDED.foreign_landing_url, "
        f"url = EXCLUDED.url, "
        f"thumbnail = EXCLUDED.thumbnail, "
        f"width = EXCLUDED.width, "
        f"height = EXCLUDED.height, "
        f"license = EXCLUDED.license, "
        f"license_version = EXCLUDED.license_version, "
        f"creator = EXCLUDED.creator, "
        f"creator_url = EXCLUDED.creator_url, "
        f"title = EXCLUDED.title, "
        f"last_synced_with_source = NOW(), "
        f"removed_from_source = 'f', "
        f"meta_data = EXCLUDED.meta_data, "
        f"watermarked = EXCLUDED.watermarked\n"
        f"WHERE {image_table}.foreign_identifier = EXCLUDED.foreign_identifier"
        f" AND {image_table}.provider = EXCLUDED.provider;"
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
