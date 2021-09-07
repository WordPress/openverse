"""
This program helps identify smithsonian unit codes which are not yet added to
the smithsonian sub-provider dictionary
"""

import logging
from textwrap import dedent

import requests
from airflow.providers.postgres.hooks.postgres import PostgresHook
from provider_api_scripts import smithsonian
from util.loader import provider_details as prov


logger = logging.getLogger(__name__)

DELAY = smithsonian.DELAY
API_KEY = smithsonian.API_KEY
API_ROOT = smithsonian.API_ROOT
UNITS_ENDPOINT = smithsonian.UNITS_ENDPOINT
PARAMS = {"api_key": API_KEY, "q": "online_media_type:Images"}
SUB_PROVIDERS = prov.SMITHSONIAN_SUB_PROVIDERS
SI_UNIT_CODE_TABLE = "smithsonian_new_unit_codes"


def initialise_unit_code_table(postgres_conn_id, unit_code_table):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Create table to store new unit codes if it does not exist
    """
    postgres.run(
        dedent(
            f"""
        CREATE TABLE IF NOT EXISTS public.{unit_code_table} (
        new_unit_code character varying(80),
        action character varying(40)
        );
        """
        )
    )

    """
    Delete old unit code entries
    """
    postgres.run(
        dedent(
            f"""
        DELETE FROM public.{unit_code_table};
        """
        )
    )


def get_new_and_outdated_unit_codes(unit_code_set, sub_prov_dict=SUB_PROVIDERS):
    sub_provider_unit_code_set = set()

    for sub_prov, unit_code_sub_set in sub_prov_dict.items():
        sub_provider_unit_code_set = sub_provider_unit_code_set.union(unit_code_sub_set)

    new_unit_codes = unit_code_set - sub_provider_unit_code_set
    outdated_unit_codes = sub_provider_unit_code_set - unit_code_set

    if bool(new_unit_codes):
        logger.info(
            f"The new unit codes {new_unit_codes} must be added to "
            f"the SMITHSONIAN_SUB_PROVIDERS dictionary"
        )

    if bool(outdated_unit_codes):
        logger.info(
            f"The outdated unit codes {outdated_unit_codes} must be "
            f"deleted from the SMITHSONIAN_SUB_PROVIDERS dictionary"
        )

    return new_unit_codes, outdated_unit_codes


def alert_unit_codes_from_api(
    postgres_conn_id,
    unit_code_table="smithsonian_new_unit_codes",
    units_endpoint=UNITS_ENDPOINT,
    query_params=PARAMS,
):
    response = requests.get(units_endpoint, params=query_params)
    unit_code_set = set(response.json().get("response", {}).get("terms", []))
    new_unit_codes, outdated_unit_codes = get_new_and_outdated_unit_codes(unit_code_set)

    initialise_unit_code_table(postgres_conn_id, unit_code_table)

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)

    """
    Populate the table with new unit codes
    """
    for new_unit_code in new_unit_codes:
        postgres.run(
            dedent(
                f"""
                INSERT INTO public.{unit_code_table}
                (new_unit_code, action)
                VALUES (
                  '{new_unit_code}', 'add'
                );
                """
            )
        )

    """
    Populate the table with outdated unit codes
    """
    for outdated_unit_code in outdated_unit_codes:
        postgres.run(
            dedent(
                f"""
                INSERT INTO public.{unit_code_table}
                (new_unit_code, action)
                VALUES (
                  '{outdated_unit_code}', 'delete'
                );
                """
            )
        )

    """
    Raise exception if human intervention is needed to update the
    SMITHSONIAN_SUB_PROVIDERS dictionary by checking the entries in the
    smithsonian_new_unit_codes table
    """
    if bool(new_unit_codes) or bool(outdated_unit_codes):
        raise Exception(
            "Please check the smithsonian_new_unit_codes table for necessary "
            "updates to the SMITHSONIAN_SUB_PROVIDERS dictionary"
        )
