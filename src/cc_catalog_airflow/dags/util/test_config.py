import os

import util.config as config

def test_paths_to_scripts_exist():
    for source in config.dag_variables:
        assert os.path.exists(config.dag_variables[source]['script'])
