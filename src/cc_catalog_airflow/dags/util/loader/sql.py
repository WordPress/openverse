import logging
from textwrap import dedent
from airflow.hooks.postgres_hook import PostgresHook
from util.loader import column_names as col
from psycopg2.errors import InvalidTextRepresentation

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
        dedent(
            f'''
            CREATE TABLE public.{load_table} (
              {col.FOREIGN_ID} character varying(3000),
              {col.LANDING_URL} character varying(1000),
              {col.DIRECT_URL} character varying(3000),
              {col.THUMBNAIL} character varying(3000),
              {col.WIDTH} integer,
              {col.HEIGHT} integer,
              {col.FILESIZE} character varying(100),
              {col.LICENSE} character varying(50),
              {col.LICENSE_VERSION} character varying(25),
              {col.CREATOR} character varying(2000),
              {col.CREATOR_URL} character varying(2000),
              {col.TITLE} character varying(5000),
              {col.META_DATA} jsonb,
              {col.TAGS} jsonb,
              {col.WATERMARKED} boolean,
              {col.PROVIDER} character varying(80),
              {col.SOURCE} character varying(80)
            );
            '''
        )
    )
    postgres.run(
        f'ALTER TABLE public.{load_table} OWNER TO {DB_USER_NAME};'
    )
    postgres.run(
        dedent(
            f'''
            CREATE INDEX IF NOT EXISTS {load_table}_{col.PROVIDER}_key
            ON public.{load_table} USING btree ({col.PROVIDER});
            '''
        )
    )
    postgres.run(
        dedent(
            f'''
            CREATE INDEX IF NOT EXISTS {load_table}_{col.FOREIGN_ID}_key
            ON public.{load_table}
            USING btree (provider, md5(({col.FOREIGN_ID})::text));
            '''
        )
    )
    postgres.run(
        dedent(
            f'''
            CREATE INDEX IF NOT EXISTS {load_table}_{col.DIRECT_URL}_key
            ON public.{load_table}
            USING btree (provider, md5(({col.DIRECT_URL})::text));
            '''
        )
    )


def load_local_data_to_intermediate_table(
        postgres_conn_id,
        tsv_file_name,
        identifier,
        max_rows_to_skip=10
):
    load_table = _get_load_table_name(identifier)
    logger.info(f'Loading {tsv_file_name} into {load_table}')

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    load_successful = False

    while not load_successful and max_rows_to_skip >= 0:
        try:
            postgres.bulk_load(f'{load_table}', tsv_file_name)
            load_successful = True

        except InvalidTextRepresentation as e:
            line_number = _get_malformed_row_in_file(str(e))
            _delete_malformed_row_in_file(tsv_file_name, line_number)

        finally:
            max_rows_to_skip = max_rows_to_skip - 1

    if not load_successful:
        raise InvalidTextRepresentation(
            'Exceeded the maximum number of allowed defective rows')

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
        dedent(
            f"""
            SELECT aws_s3.table_import_from_s3(
              '{load_table}',
              '',
              'DELIMITER E''\t''',
              '{bucket}',
              '{s3_key}',
              'us-east-1'
            );
            """
        )
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
        f'DELETE FROM {load_table} WHERE {col.LANDING_URL} IS NULL;'
    )
    postgres_hook.run(
        f'DELETE FROM {load_table} WHERE {col.FOREIGN_ID} IS NULL;'
    )
    postgres_hook.run(
        dedent(
            f'''
            DELETE FROM {load_table} p1
            USING {load_table} p2
            WHERE
              p1.ctid < p2.ctid
              AND p1.{col.PROVIDER} = p2.{col.PROVIDER}
              AND p1.{col.FOREIGN_ID} = p2.{col.FOREIGN_ID};
            '''
        )
    )


def upsert_records_to_image_table(
        postgres_conn_id,
        identifier,
        image_table=IMAGE_TABLE_NAME
):

    def _newest_non_null(column):
        return f'{column} = COALESCE(EXCLUDED.{column}, old.{column})'

    def _merge_jsonb_objects(column):
        """
        This function returns SQL that merges the top-level keys of the
        a JSONB column, taking the newest available non-null value.
        """
        return f'''{column} = COALESCE(
            jsonb_strip_nulls(old.{column})
              || jsonb_strip_nulls(EXCLUDED.{column}),
            EXCLUDED.{column},
            old.{column}
          )'''

    def _merge_jsonb_arrays(column):
        return f'''{column} = COALESCE(
            (
              SELECT jsonb_agg(DISTINCT x)
              FROM jsonb_array_elements(old.{column} || EXCLUDED.{column}) t(x)
            ),
            EXCLUDED.{column},
            old.{column}
          )'''

    load_table = _get_load_table_name(identifier)
    logger.info(f'Upserting new records into {image_table}.')
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    column_inserts = {
        col.CREATED_ON: NOW,
        col.UPDATED_ON: NOW,
        col.PROVIDER: col.PROVIDER,
        col.SOURCE: col.SOURCE,
        col.FOREIGN_ID: col.FOREIGN_ID,
        col.LANDING_URL: col.LANDING_URL,
        col.DIRECT_URL: col.DIRECT_URL,
        col.THUMBNAIL: col.THUMBNAIL,
        col.WIDTH: col.WIDTH,
        col.HEIGHT: col.HEIGHT,
        col.LICENSE: col.LICENSE,
        col.LICENSE_VERSION: col.LICENSE_VERSION,
        col.CREATOR: col.CREATOR,
        col.CREATOR_URL: col.CREATOR_URL,
        col.TITLE: col.TITLE,
        col.LAST_SYNCED: NOW,
        col.REMOVED: FALSE,
        col.META_DATA: col.META_DATA,
        col.TAGS: col.TAGS,
        col.WATERMARKED: col.WATERMARKED
    }
    upsert_query = dedent(
        f'''
        INSERT INTO {image_table} AS old ({', '.join(column_inserts.keys())})
        SELECT {', '.join(column_inserts.values())}
        FROM {load_table}
        ON CONFLICT ({col.PROVIDER}, md5({col.FOREIGN_ID}))
        DO UPDATE SET
          {col.UPDATED_ON} = {NOW},
          {col.LAST_SYNCED} = {NOW},
          {col.REMOVED} = {FALSE},
          {_newest_non_null(col.LANDING_URL)},
          {_newest_non_null(col.DIRECT_URL)},
          {_newest_non_null(col.THUMBNAIL)},
          {_newest_non_null(col.WIDTH)},
          {_newest_non_null(col.HEIGHT)},
          {_newest_non_null(col.LICENSE)},
          {_newest_non_null(col.LICENSE_VERSION)},
          {_newest_non_null(col.CREATOR)},
          {_newest_non_null(col.CREATOR_URL)},
          {_newest_non_null(col.TITLE)},
          {_newest_non_null(col.WATERMARKED)},
          {_merge_jsonb_objects(col.META_DATA)},
          {_merge_jsonb_arrays(col.TAGS)}
        '''
    )
    postgres.run(upsert_query)


def drop_load_table(postgres_conn_id, identifier):
    load_table = _get_load_table_name(identifier)
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f'DROP TABLE {load_table};')


def _get_load_table_name(
        identifier,
        load_table_name_stub=LOAD_TABLE_NAME_STUB,
):
    return f'{load_table_name_stub}{identifier}'


def _get_malformed_row_in_file(error_msg):
    error_list = error_msg.splitlines()
    copy_error = next(
        (line for line in error_list if line.startswith('COPY')), None
    )
    assert copy_error is not None

    line_number = int(copy_error.split('line ')[1].split(',')[0])

    return line_number


def _delete_malformed_row_in_file(tsv_file_name, line_number):
    with open(tsv_file_name, "r") as read_obj:
        lines = read_obj.readlines()

    with open(tsv_file_name, "w") as write_obj:
        for index, line in enumerate(lines):
            if index + 1 != line_number:
                write_obj.write(line)

