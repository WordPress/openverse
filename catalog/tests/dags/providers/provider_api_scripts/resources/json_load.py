import json
from collections.abc import Callable
from pathlib import Path


def make_resource_json_func(folder_name: str) -> Callable[[str], dict]:
    """
    Given the name of a folder inside the resources folder returns
    a function that takes a json file name within the given folder
    and returns the contents of that json file as a dictionary.

    Args:
        folder_name (str): name of a folder inside the resources folder
        (tests/dags/providers/provider_api_scripts/resources/[folder_name]).

    Returns:
        Callable[[str], dict]: A function that when given a json
        resource name as a string returns that json resource as a dictionary.

    Example:
        json_func_ex = make_resource_json_func("brooklynmuseum")
        json_dict = json_func_ex("cc_license_info.json")
        assert json_dict["public_name"] == "Creative Commons-BY" # True

    """
    resources = Path(__file__).parent / folder_name

    # Check if the given resource path is a valid
    if not Path.is_dir(resources):
        raise FileNotFoundError(f"Folder not found at given path {resources}")

    def get_resource_json(resource_name: str) -> dict:
        return json.loads((resources / resource_name).read_text())

    return get_resource_json
