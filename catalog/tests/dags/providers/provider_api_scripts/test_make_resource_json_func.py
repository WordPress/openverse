import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)


_get_resource_json = make_resource_json_func("brooklynmuseum")


def test_docstring_example():
    json_dict = _get_resource_json("cc_license_info.json")
    assert json_dict["public_name"] == "Creative Commons-BY"


def test_folder_not_found_error():
    with pytest.raises(FileNotFoundError):
        make_resource_json_func("foobar")
