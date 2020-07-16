"""
This program helps identify smithsonian unit codes which are not yet added to
the smithsonian sub-provider dictionary
"""

import logging
import requests
import os

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


def alert_new_unit_codes(unit_code_set,
                         sub_prov_dict=SUB_PROVIDERS):
  sub_provider_unit_code_set = set()

  for sub_prov, unit_code_sub_set in sub_prov_dict.items():
    sub_provider_unit_code_set = \
      sub_provider_unit_code_set.union(unit_code_sub_set)

  new_unit_codes = unit_code_set - sub_provider_unit_code_set

  if len(new_unit_codes) > 0:
    logger.info(f'The new unit codes {new_unit_codes} must be added to '
                f'the SMITHSONIAN_SUB_PROVIDERS dictionary')

  return new_unit_codes


def alert_unit_codes_from_api(units_endpoint=UNITS_ENDPOINT,
                              query_params=PARAMS):
  response = requests.get(
      units_endpoint,
      params=query_params
  )
  unit_code_set = set(response.json().get('response', {}).get('terms', []))

  return bool(alert_new_unit_codes(unit_code_set))

