import logging
from functools import cache
from pathlib import Path

import yaml


log = logging.getLogger(__name__)

CURR_FILE = Path(__file__).resolve()
ROOT_DIR = CURR_FILE.parent.parent.parent


@cache
def get_data(file_name: str) -> dict:
    """
    Access YAML files in the `data/` directory as Python objects.

    Calls to the function with the same file name will be cached for performance.

    :param file_name: the name of the YAML file to read
    :return: the contents of the YAML file as a Python object
    """

    data_file: str = str(ROOT_DIR.joinpath("data", file_name))
    log.info(f"Reading file {data_file}")
    return yaml.safe_load(open(data_file, encoding="utf-8"))
