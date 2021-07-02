import logging
import json
from textwrap import dedent
from airflow.providers.postgres.hooks.postgres import PostgresHook
from util.loader import column_names as col
from util.loader import provider_details as prov
from psycopg2.errors import InvalidTextRepresentation

from util.loader.paths import _extract_media_type

logger = logging.getLogger(__name__)

LOAD_TABLE_NAME_STUB = 'provider_data_'
IMAGE_TABLE_NAME = 'image'
AUDIO_TABLE_NAME = 'audio'
DB_USER_NAME = 'deploy'
NOW = 'NOW()'
FALSE = "'f'"
OLDEST_PER_PROVIDER = {
    prov.FLICKR_DEFAULT_PROVIDER: '6 months 18 days',
    prov.EUROPEANA_DEFAULT_PROVIDER: '3 months 9 days',
    prov.WIKIMEDIA_DEFAULT_PROVIDER: '6 months 18 days',
    prov.SMITHSONIAN_DEFAULT_PROVIDER: '8 days',
    prov.BROOKLYN_DEFAULT_PROVIDER: '1 month 3 days',
    prov.CLEVELAND_DEFAULT_PROVIDER: '1 month 3 days',
    prov.VICTORIA_DEFAULT_PROVIDER: '1 month 3 days',
    prov.NYPL_DEFAULT_PROVIDER: '1 month 3 days',
    prov.RAWPIXEL_DEFAULT_PROVIDER: '1 month 3 days',
    prov.SCIENCE_DEFAULT_PROVIDER: '1 month 3 days',
    prov.STATENS_DEFAULT_PROVIDER: '1 month 3 days'
}


def create_loading_table(
        postgres_conn_id,
        identifier,
        ti,
):
    """
    Create intermediary table and indices if they do not exist
    """
    media_type = ti.xcom_pull(
        task_ids='stage_oldest_tsv_file', key='media_type'
    )
    if media_type is None:
        media_type = 'image'
    load_table = _get_load_table_name(identifier, media_type=media_type)
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    if media_type == 'audio':
        table_creation_query = dedent(
            f'''
            CREATE TABLE public.{load_table} (
              {col.FOREIGN_ID} character varying(3000),
              {col.LANDING_URL} character varying(1000),
              {col.DIRECT_URL} character varying(3000),
              {col.THUMBNAIL} character varying(3000),
              {col.FILESIZE} integer,
              {col.LICENSE} character varying(50),
              {col.LICENSE_VERSION} character varying(25),
              {col.CREATOR} character varying(2000),
              {col.CREATOR_URL} character varying(2000),
              {col.TITLE} character varying(5000),
              {col.META_DATA} jsonb,
              {col.TAGS} jsonb,
              {col.PROVIDER} character varying(80),
              {col.SOURCE} character varying(80),
              {col.INGESTION_TYPE} character varying(80),
              {col.DURATION} integer,
              {col.BIT_RATE} integer,
              {col.SAMPLE_RATE} integer,
              {col.CATEGORY} character varying(100),
              {col.GENRE} jsonb,
              {col.AUDIO_SET} jsonb,
              {col.ALT_AUDIO_FILES} jsonb
            );
            '''
        )
    else:
        table_creation_query = dedent(
            f'''
            CREATE TABLE public.{load_table} (
              {col.FOREIGN_ID} character varying(3000),
              {col.LANDING_URL} character varying(1000),
              {col.DIRECT_URL} character varying(3000),
              {col.THUMBNAIL} character varying(3000),
              {col.WIDTH} integer,
              {col.HEIGHT} integer,
              {col.FILESIZE} integer,
              {col.LICENSE} character varying(50),
              {col.LICENSE_VERSION} character varying(25),
              {col.CREATOR} character varying(2000),
              {col.CREATOR_URL} character varying(2000),
              {col.TITLE} character varying(5000),
              {col.META_DATA} jsonb,
              {col.TAGS} jsonb,
              {col.WATERMARKED} boolean,
              {col.PROVIDER} character varying(80),
              {col.SOURCE} character varying(80),
              {col.INGESTION_TYPE} character varying(80)
            );
            '''
        )
    postgres.run(table_creation_query)
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
    media_type = _extract_media_type(tsv_file_name)
    load_table = _get_load_table_name(identifier, media_type=media_type)
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
        identifier,
        media_type='image'
):
    load_table = _get_load_table_name(identifier, media_type=media_type)
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
    """
    Necessary for old TSV files that have not been cleaned up,
    using `MediaStore` class:
    Removes any rows without any of the required fields:
    `url`, `license`, `license_version`, `foreign_id`.
    Also removes any duplicate rows that have the same `provider`
    and `foreign_id`.
    """
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


def upsert_records_to_db_table(
        postgres_conn_id,
        identifier,
        db_table=None,
        media_type='image',
):
    def _newest_non_null(column: str) -> str:
        return f'{column} = COALESCE(EXCLUDED.{column}, old.{column})'

    def _merge_jsonb_objects(column: str) -> str:
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

    def _merge_jsonb_arrays(column: str) -> str:
        return f'''{column} = COALESCE(
            (
              SELECT jsonb_agg(DISTINCT x)
              FROM jsonb_array_elements(old.{column} || EXCLUDED.{column}) t(x)
            ),
            EXCLUDED.{column},
            old.{column}
          )'''
    if db_table is None:
        db_table = AUDIO_TABLE_NAME \
            if media_type == 'audio' else IMAGE_TABLE_NAME

    load_table = _get_load_table_name(identifier, media_type=media_type)
    logger.info(f'Upserting new records into {db_table}.')
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    column_inserts = {
            col.CREATED_ON: NOW,
            col.UPDATED_ON: NOW,
            col.INGESTION_TYPE: col.INGESTION_TYPE,
            col.PROVIDER: col.PROVIDER,
            col.SOURCE: col.SOURCE,
            col.FOREIGN_ID: col.FOREIGN_ID,
            col.LANDING_URL: col.LANDING_URL,
            col.DIRECT_URL: col.DIRECT_URL,
            col.THUMBNAIL: col.THUMBNAIL,
            col.FILESIZE: col.FILESIZE,
            col.LICENSE: col.LICENSE,
            col.LICENSE_VERSION: col.LICENSE_VERSION,
            col.CREATOR: col.CREATOR,
            col.CREATOR_URL: col.CREATOR_URL,
            col.TITLE: col.TITLE,
            col.LAST_SYNCED: NOW,
            col.REMOVED: FALSE,
            col.META_DATA: col.META_DATA,
            col.TAGS: col.TAGS,
            col.WATERMARKED: col.WATERMARKED,
    }
    if media_type == 'audio':
        column_inserts.update({
            col.DURATION: col.DURATION,
            col.BIT_RATE: col.BIT_RATE,
            col.SAMPLE_RATE: col.SAMPLE_RATE,
            col.CATEGORY: col.CATEGORY,
            col.GENRE: col.GENRE,
            col.AUDIO_SET: col.AUDIO_SET,
            col.ALT_AUDIO_FILES: col.ALT_AUDIO_FILES,
        })
    else:
        column_inserts.update({
            col.WIDTH: col.WIDTH,
            col.HEIGHT: col.HEIGHT,
        })
    if media_type == 'audio':
        media_specific_upsert_query = (
            f'''{_newest_non_null(col.DURATION)},
            {_newest_non_null(col.BIT_RATE)},
            {_newest_non_null(col.SAMPLE_RATE)},
            {_newest_non_null(col.CATEGORY)},
            {_merge_jsonb_arrays(col.GENRE)},
            {_merge_jsonb_objects(col.AUDIO_SET)},
            {_merge_jsonb_objects(col.ALT_AUDIO_FILES)}
            '''
        )
    else:
        media_specific_upsert_query = (
            f'''{_newest_non_null(col.WIDTH)},
            {_newest_non_null(col.HEIGHT)}'''
        )
    upsert_query = dedent(
        f'''
        INSERT INTO {db_table} AS old ({', '.join(column_inserts.keys())})
        SELECT {', '.join(column_inserts.values())}
        FROM {load_table}
        ON CONFLICT ({col.PROVIDER}, md5({col.FOREIGN_ID}))
        DO UPDATE SET
          {col.UPDATED_ON} = {NOW},
          {col.LAST_SYNCED} = {NOW},
          {col.REMOVED} = {FALSE},
          {_newest_non_null(col.INGESTION_TYPE)},
          {_newest_non_null(col.SOURCE)},
          {_newest_non_null(col.LANDING_URL)},
          {_newest_non_null(col.DIRECT_URL)},
          {_newest_non_null(col.THUMBNAIL)},
          {_newest_non_null(col.FILESIZE)},
          {_newest_non_null(col.LICENSE)},
          {_newest_non_null(col.LICENSE_VERSION)},
          {_newest_non_null(col.CREATOR)},
          {_newest_non_null(col.CREATOR_URL)},
          {_newest_non_null(col.TITLE)},
          {_merge_jsonb_objects(col.META_DATA)},
          {_merge_jsonb_arrays(col.TAGS)},
          {_newest_non_null(col.WATERMARKED)},
          {media_specific_upsert_query}
        '''
    )
    postgres.run(upsert_query)


def overwrite_records_in_db_table(
        postgres_conn_id,
        identifier,
        db_table=None,
        media_type='image'
):
    if db_table is None:
        db_table = AUDIO_TABLE_NAME \
            if media_type == 'audio' else IMAGE_TABLE_NAME
    load_table = _get_load_table_name(identifier, media_type=media_type)
    logger.info(f'Updating records in {db_table}.')
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    if media_type == 'audio':
        columns_to_update = [
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.WATERMARKED,
            col.DURATION,
            col.BIT_RATE,
            col.SAMPLE_RATE,
            col.CATEGORY,
            col.GENRE,
            col.AUDIO_SET,
            col.ALT_AUDIO_FILES,
        ]
    else:
        columns_to_update = [
            col.LANDING_URL,
            col.DIRECT_URL,
            col.THUMBNAIL,
            col.WIDTH,
            col.HEIGHT,
            col.FILESIZE,
            col.LICENSE,
            col.LICENSE_VERSION,
            col.CREATOR,
            col.CREATOR_URL,
            col.TITLE,
            col.META_DATA,
            col.TAGS,
            col.WATERMARKED,
        ]
    update_set_string = ',\n'.join(
        [f'{column} = {load_table}.{column}' for column in columns_to_update]
    )

    update_query = dedent(
        f'''
        UPDATE {db_table}
        SET
        {update_set_string}
        FROM {load_table}
        WHERE
          {db_table}.{col.PROVIDER} = {load_table}.{col.PROVIDER}
          AND
          md5({db_table}.{col.FOREIGN_ID})
            = md5({load_table}.{col.FOREIGN_ID});
        '''
    )
    postgres.run(update_query)


def drop_load_table(postgres_conn_id, identifier, ti):
    media_type = ti.xcom_pull(
        task_ids='stage_oldest_tsv_file', key='media_type'
    )
    if media_type is None:
        media_type = 'image'
    load_table = _get_load_table_name(identifier, media_type=media_type)
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f'DROP TABLE {load_table};')


def _get_load_table_name(
        identifier: str,
        media_type: str = 'image',
        load_table_name_stub: str = LOAD_TABLE_NAME_STUB,
) -> str:
    return f'{load_table_name_stub}{media_type}_{identifier}'


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


def _create_temp_flickr_sub_prov_table(
        postgres_conn_id,
        temp_table='temp_flickr_sub_prov_table'
):
    """
    Drop the temporary table if it already exists
    """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f'DROP TABLE IF EXISTS public.{temp_table};')

    """
    Create intermediary table for sub provider migration
    """
    postgres.run(
        dedent(
            f'''
            CREATE TABLE public.{temp_table} (
              {col.CREATOR_URL} character varying(2000),
              sub_provider character varying(80)
            );
            '''
        )
    )

    postgres.run(
        f'ALTER TABLE public.{temp_table} OWNER TO {DB_USER_NAME};'
    )

    """
    Populate the intermediary table with the sub providers of interest
    """
    for sub_prov, user_id_set in prov.FLICKR_SUB_PROVIDERS.items():
        for user_id in user_id_set:
            creator_url = prov.FLICKR_PHOTO_URL_BASE + user_id
            postgres.run(
                dedent(
                    f'''
                    INSERT INTO public.{temp_table} (
                      {col.CREATOR_URL},
                      sub_provider
                    )
                    VALUES (
                      '{creator_url}',
                      '{sub_prov}'
                    );
                    '''
                )
            )

    return temp_table


def update_flickr_sub_providers(
  postgres_conn_id,
  image_table=IMAGE_TABLE_NAME,
  default_provider=prov.FLICKR_DEFAULT_PROVIDER,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    temp_table = _create_temp_flickr_sub_prov_table(postgres_conn_id)

    select_query = dedent(
        f'''
        SELECT
        {col.FOREIGN_ID} AS foreign_id,
        public.{temp_table}.sub_provider AS sub_provider
        FROM {image_table}
        INNER JOIN public.{temp_table}
        ON
        {image_table}.{col.CREATOR_URL} = public.{temp_table}.{
        col.CREATOR_URL}
        AND
        {image_table}.{col.PROVIDER} = '{default_provider}';
        '''
    )

    selected_records = postgres.get_records(select_query)
    logger.info(f'Updating {len(selected_records)} records')

    for row in selected_records:
        foreign_id = row[0]
        sub_provider = row[1]
        postgres.run(
            dedent(
                f'''
                UPDATE {image_table}
                SET {col.SOURCE} = '{sub_provider}'
                WHERE
                {image_table}.{col.PROVIDER} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID}) = MD5('{foreign_id}');
                '''
            )
        )

    """
    Drop the temporary table
    """
    postgres.run(f'DROP TABLE public.{temp_table};')


def _create_temp_europeana_sub_prov_table(
        postgres_conn_id,
        temp_table='temp_eur_sub_prov_table'
):
    """
    Drop the temporary table if it already exists
    """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f'DROP TABLE IF EXISTS public.{temp_table};')

    """
    Create intermediary table for sub provider migration
    """
    postgres.run(
        dedent(
            f'''
            CREATE TABLE public.{temp_table} (
              data_provider character varying(120),
              sub_provider character varying(80)
            );
            '''
        )
    )

    postgres.run(
        f'ALTER TABLE public.{temp_table} OWNER TO {DB_USER_NAME};'
    )

    """
    Populate the intermediary table with the sub providers of interest
    """
    for sub_prov, data_provider in prov.EUROPEANA_SUB_PROVIDERS.items():
        postgres.run(
            dedent(
                f'''
                INSERT INTO public.{temp_table} (
                  data_provider,
                  sub_provider
                )
                VALUES (
                  '{data_provider}',
                  '{sub_prov}'
                );
                '''
            )
        )

    return temp_table


def update_europeana_sub_providers(
  postgres_conn_id,
  image_table=IMAGE_TABLE_NAME,
  default_provider=prov.EUROPEANA_DEFAULT_PROVIDER,
  sub_providers=prov.EUROPEANA_SUB_PROVIDERS
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    temp_table = _create_temp_europeana_sub_prov_table(postgres_conn_id)

    select_query = dedent(
        f'''
        SELECT L.foreign_id, L.data_providers, R.sub_provider
        FROM(
        SELECT
        {col.FOREIGN_ID} AS foreign_id,
        {col.META_DATA} ->> 'dataProvider' AS data_providers,
        {col.META_DATA}
        FROM {image_table}
        WHERE {col.PROVIDER} = '{default_provider}'
        ) L INNER JOIN
        {temp_table} R ON
        L.{col.META_DATA} ->'dataProvider' ? R.data_provider;
        '''
    )

    selected_records = postgres.get_records(select_query)

    """
    Update each selected row if it corresponds to only one sub-provider.
    Otherwise an exception is thrown
    """
    for row in selected_records:
        foreign_id = row[0]
        data_providers = json.loads(row[1])
        sub_provider = row[2]

        eligible_sub_providers = {s for s in sub_providers if sub_providers[s]
                                  in data_providers}
        if len(eligible_sub_providers) > 1:
            raise Exception(f"More than one sub-provider identified for the "
                            f"image with foreign ID {foreign_id}")

        assert len(eligible_sub_providers) == 1
        assert eligible_sub_providers.pop() == sub_provider

        postgres.run(
            dedent(
                f'''
                UPDATE {image_table}
                SET {col.SOURCE} = '{sub_provider}'
                WHERE
                {image_table}.{col.PROVIDER} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID}) = MD5('{foreign_id}');
                '''
            )
        )

    """
    Drop the temporary table
    """
    postgres.run(f'DROP TABLE public.{temp_table};')


def update_smithsonian_sub_providers(
  postgres_conn_id,
  image_table=IMAGE_TABLE_NAME,
  default_provider=prov.SMITHSONIAN_DEFAULT_PROVIDER,
  sub_providers=prov.SMITHSONIAN_SUB_PROVIDERS
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Select all records where the source value is not yet updated
    """
    select_query = dedent(
        f'''
        SELECT {col.FOREIGN_ID},
        {col.META_DATA} ->> 'unit_code' AS unit_code
        FROM {image_table}
        WHERE
        {col.PROVIDER} = '{default_provider}'
        AND
        {col.SOURCE} = '{default_provider}';
        '''
    )

    selected_records = postgres.get_records(select_query)

    """
    Set the source value of each selected row to the sub-provider value
    corresponding to unit code. If the unit code is unknown, an error is thrown
    """
    for row in selected_records:
        foreign_id = row[0]
        unit_code = row[1]

        source = next((s for s in sub_providers if unit_code in
                       sub_providers[s]), None)
        if source is None:
            raise Exception(
                f"An unknown unit code value {unit_code} encountered ")

        postgres.run(
            dedent(
                f'''
                UPDATE {image_table}
                SET {col.SOURCE} = '{source}'
                WHERE
                {image_table}.{col.PROVIDER} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID}) = MD5('{foreign_id}');
                '''
            )
        )


def expire_old_images(
  postgres_conn_id,
  provider,
  image_table=IMAGE_TABLE_NAME
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    if provider not in OLDEST_PER_PROVIDER:
        raise Exception(
            f"Provider value {provider} not defined in the "
            f"OLDEST_PER_PROVIDER dictionary")

    """
    Select all records that are outdated
    """
    select_query = dedent(
        f'''
        SELECT {col.FOREIGN_ID}
        FROM {image_table}
        WHERE
        {col.PROVIDER} = '{provider}'
        AND
        {col.UPDATED_ON} < {NOW} - INTERVAL '{OLDEST_PER_PROVIDER[provider]}';
        '''
    )

    selected_records = postgres.get_records(select_query)

    """
    Set the 'removed_from_source' value of each selected row to True to
    indicate that those images are outdated
    """
    for row in selected_records:
        foreign_id = row[0]

        postgres.run(
            dedent(
                f'''
                UPDATE {image_table}
                SET {col.REMOVED} = 't'
                WHERE
                {image_table}.{col.PROVIDER} = '{provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID}) = MD5('{foreign_id}');
                '''
            )
        )
