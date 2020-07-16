import pytest
from util.loader import smithsonian_unit_codes as si


def test_alert_new_unit_codes():
  unit_code_set = {'a', 'b', 'c', 'd'}
  sub_prov_dict = {'sub_prov1': {'a', 'c'}, 'sub_prov2': {'b'}}

  assert si.alert_new_unit_codes(unit_code_set, sub_prov_dict) == {'d'}


@pytest.mark.enable_socket
def test_alert_unit_codes_from_api():
  assert si.alert_unit_codes_from_api() in (True, False)
