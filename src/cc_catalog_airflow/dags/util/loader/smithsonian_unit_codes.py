"""
This program helps identify smithsonian unit codes which are not yet added to
the smithsonian sub-provider dictionary
"""

import logging
import requests
import os

from textwrap import dedent
from airflow.hooks.postgres_hook import PostgresHook
from util.loader import provider_details as prov

logger = logging.getLogger(__name__)

DELAY = 5.0
API_KEY = os.getenv('DATA_GOV_API_KEY')
API_ROOT = 'https://api.si.edu/openaccess/api/v1.0/'
UNITS_ENDPOINT = API_ROOT + 'terms/unit_code'
PARAMS = {
    'api_key': API_KEY,
    'q': 'online_media_type:Images'
}
SUB_PROVIDERS = prov.SMITHSONIAN_SUB_PROVIDERS

DB_USER_NAME = 'deploy'
SI_UNIT_CODE_TABLE = 'smithsonian_new_unit_codes'


def initialise_unit_code_table(postgres_conn_id, unit_code_table):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Create table to store new unit codes if it does not exist
    """
    postgres.run(
      dedent(
        f'''
        CREATE TABLE IF NOT EXISTS public.{unit_code_table} (
        new_unit_code character varying(80),
        action character varying(40)
        );
        '''
      )
    )

    postgres.run(
      f'ALTER TABLE public.{unit_code_table} OWNER TO {DB_USER_NAME};'
    )

    """
    Delete old unit code entries
    """
    postgres.run(
      dedent(
        f'''
        DELETE FROM public.{unit_code_table};
        '''
      )
    )


def get_new_and_outdated_unit_codes(unit_code_set,
                                    sub_prov_dict=SUB_PROVIDERS):
    sub_provider_unit_code_set = set()

    for sub_prov, unit_code_sub_set in sub_prov_dict.items():
        sub_provider_unit_code_set = \
          sub_provider_unit_code_set.union(unit_code_sub_set)

    new_unit_codes = unit_code_set - sub_provider_unit_code_set
    outdated_unit_codes = sub_provider_unit_code_set - unit_code_set

    if bool(new_unit_codes):
        logger.info(f'The new unit codes {new_unit_codes} must be added to '
                    f'the SMITHSONIAN_SUB_PROVIDERS dictionary')

    if bool(outdated_unit_codes):
        logger.info(f'The outdated unit codes {outdated_unit_codes} must be '
                    f'deleted from the SMITHSONIAN_SUB_PROVIDERS dictionary')

    return new_unit_codes, outdated_unit_codes


def alert_unit_codes_from_api(postgres_conn_id,
                              unit_code_table='smithsonian_new_unit_codes',
                              units_endpoint=UNITS_ENDPOINT,
                              query_params=PARAMS):
    response = requests.get(
        units_endpoint,
        params=query_params
    )
    unit_code_set = set(response.json().get('response', {}).get('terms', []))
    new_unit_codes, outdated_unit_codes = get_new_and_outdated_unit_codes(
      unit_code_set)

    initialise_unit_code_table(postgres_conn_id, unit_code_table)

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Populate the table with new unit codes
    """
    for new_unit_code in new_unit_codes:
        postgres.run(
            dedent(
                f'''
                INSERT INTO public.{unit_code_table}
                (new_unit_code, action)
                VALUES (
                  '{new_unit_code}', 'add'
                );
                '''
            )
        )

    """
    Populate the table with outdated unit codes
    """
    for outdated_unit_code in outdated_unit_codes:
        postgres.run(
            dedent(
                f'''
                INSERT INTO public.{unit_code_table}
                (new_unit_code, action)
                VALUES (
                  '{outdated_unit_code}', 'delete'
                );
                '''
            )
        )
