import json
from textwrap import dedent

from airflow.providers.postgres.hooks.postgres import PostgresHook
from storage import columns as col
from util.constants import IMAGE
from util.loader import provider_details as prov
from util.loader.sql import DB_USER_NAME, TABLE_NAMES, logger


def _create_temp_flickr_sub_prov_table(
    postgres_conn_id, temp_table="temp_flickr_sub_prov_table"
):
    """
    Drop the temporary table if it already exists
    """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f"DROP TABLE IF EXISTS public.{temp_table};")

    """
    Create intermediary table for sub provider migration
    """
    postgres.run(
        dedent(
            f"""
            CREATE TABLE public.{temp_table} (
              {col.CREATOR_URL.db_name} character varying(2000),
              sub_provider character varying(80)
            );
            """
        )
    )

    postgres.run(f"ALTER TABLE public.{temp_table} OWNER TO {DB_USER_NAME};")

    """
    Populate the intermediary table with the sub providers of interest
    """
    for sub_prov, user_id_set in prov.FLICKR_SUB_PROVIDERS.items():
        for user_id in user_id_set:
            creator_url = prov.FLICKR_PHOTO_URL_BASE + user_id
            postgres.run(
                dedent(
                    f"""
                    INSERT INTO public.{temp_table} (
                      {col.CREATOR_URL.db_name},
                      sub_provider
                    )
                    VALUES (
                      '{creator_url}',
                      '{sub_prov}'
                    );
                    """
                )
            )

    return temp_table


def update_flickr_sub_providers(
    postgres_conn_id,
    image_table=TABLE_NAMES[IMAGE],
    default_provider=prov.FLICKR_DEFAULT_PROVIDER,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    temp_table = _create_temp_flickr_sub_prov_table(postgres_conn_id)

    select_query = dedent(
        f"""
        SELECT
        {col.FOREIGN_ID.db_name} AS foreign_id,
        public.{temp_table}.sub_provider AS sub_provider
        FROM {image_table}
        INNER JOIN public.{temp_table}
        ON
        {image_table}.{col.CREATOR_URL.db_name} = public.{temp_table}.{
        col.CREATOR_URL.db_name}
        AND
        {image_table}.{col.PROVIDER.db_name} = '{default_provider}';
        """
    )

    selected_records = postgres.get_records(select_query)
    logger.info(f"Updating {len(selected_records)} records")

    for row in selected_records:
        foreign_id = row[0]
        sub_provider = row[1]
        postgres.run(
            dedent(
                f"""
                UPDATE {image_table}
                SET {col.SOURCE.db_name} = '{sub_provider}'
                WHERE
                {image_table}.{col.PROVIDER.db_name} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID.db_name}) = MD5('{foreign_id}');
                """
            )
        )

    """
    Drop the temporary table
    """
    postgres.run(f"DROP TABLE public.{temp_table};")


def _create_temp_europeana_sub_prov_table(
    postgres_conn_id, temp_table="temp_eur_sub_prov_table"
):
    """
    Drop the temporary table if it already exists
    """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f"DROP TABLE IF EXISTS public.{temp_table};")

    """
    Create intermediary table for sub provider migration
    """
    postgres.run(
        dedent(
            f"""
            CREATE TABLE public.{temp_table} (
              data_provider character varying(120),
              sub_provider character varying(80)
            );
            """
        )
    )

    postgres.run(f"ALTER TABLE public.{temp_table} OWNER TO {DB_USER_NAME};")

    """
    Populate the intermediary table with the sub providers of interest
    """
    for sub_prov, data_provider in prov.EUROPEANA_SUB_PROVIDERS.items():
        postgres.run(
            dedent(
                f"""
                INSERT INTO public.{temp_table} (
                  data_provider,
                  sub_provider
                )
                VALUES (
                  '{data_provider}',
                  '{sub_prov}'
                );
                """
            )
        )

    return temp_table


def update_europeana_sub_providers(
    postgres_conn_id,
    image_table=TABLE_NAMES[IMAGE],
    default_provider=prov.EUROPEANA_DEFAULT_PROVIDER,
    sub_providers=prov.EUROPEANA_SUB_PROVIDERS,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    temp_table = _create_temp_europeana_sub_prov_table(postgres_conn_id)

    select_query = dedent(
        f"""
        SELECT L.foreign_id, L.data_providers, R.sub_provider
        FROM(
        SELECT
        {col.FOREIGN_ID.db_name} AS foreign_id,
        {col.META_DATA.db_name} ->> 'dataProvider' AS data_providers,
        {col.META_DATA.db_name}
        FROM {image_table}
        WHERE {col.PROVIDER.db_name} = '{default_provider}'
        ) L INNER JOIN
        {temp_table} R ON
        L.{col.META_DATA.db_name} ->'dataProvider' ? R.data_provider;
        """
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

        eligible_sub_providers = {
            s for s in sub_providers if sub_providers[s] in data_providers
        }
        if len(eligible_sub_providers) > 1:
            raise Exception(
                f"More than one sub-provider identified for the "
                f"image with foreign ID {foreign_id}"
            )

        assert len(eligible_sub_providers) == 1
        assert eligible_sub_providers.pop() == sub_provider

        postgres.run(
            dedent(
                f"""
                UPDATE {image_table}
                SET {col.SOURCE.db_name} = '{sub_provider}'
                WHERE
                {image_table}.{col.PROVIDER.db_name} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID.db_name}) = MD5('{foreign_id}');
                """
            )
        )

    """
    Drop the temporary table
    """
    postgres.run(f"DROP TABLE public.{temp_table};")


def update_smithsonian_sub_providers(
    postgres_conn_id,
    image_table=TABLE_NAMES[IMAGE],
    default_provider=prov.SMITHSONIAN_DEFAULT_PROVIDER,
    sub_providers=prov.SMITHSONIAN_SUB_PROVIDERS,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Select all records where the source value is not yet updated
    """
    select_query = dedent(
        f"""
        SELECT {col.FOREIGN_ID.db_name},
        {col.META_DATA.db_name} ->> 'unit_code' AS unit_code
        FROM {image_table}
        WHERE
        {col.PROVIDER.db_name} = '{default_provider}'
        AND
        {col.SOURCE.db_name} = '{default_provider}';
        """
    )

    selected_records = postgres.get_records(select_query)

    """
    Set the source value of each selected row to the sub-provider value
    corresponding to unit code. If the unit code is unknown, an error is thrown
    """
    for row in selected_records:
        foreign_id = row[0]
        unit_code = row[1]

        source = next((s for s in sub_providers if unit_code in sub_providers[s]), None)
        if source is None:
            raise Exception(f"An unknown unit code value {unit_code} encountered ")

        postgres.run(
            dedent(
                f"""
                UPDATE {image_table}
                SET {col.SOURCE.db_name} = '{source}'
                WHERE
                {image_table}.{col.PROVIDER.db_name} = '{default_provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID.db_name}) = MD5('{foreign_id}');
                """
            )
        )
