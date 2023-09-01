import re
from pathlib import Path

import pytest
from popularity.popularity_refresh_types import POPULARITY_REFRESH_CONFIGS


DDL_DEFINITIONS_PATH = Path(__file__).parents[4] / "docker" / "upstream_db"


@pytest.mark.parametrize(
    "ddl_filename, metrics",
    [
        (
            "0004_openledger_image_view.sql",
            POPULARITY_REFRESH_CONFIGS[0].popularity_metrics,
        ),
        (
            "0007_openledger_audio_view.sql",
            POPULARITY_REFRESH_CONFIGS[1].popularity_metrics,
        ),
    ],
)
def test_ddl_matches_definitions(ddl_filename, metrics):
    ddl = (DDL_DEFINITIONS_PATH / ddl_filename).read_text()
    if not (
        match := re.search(
            r"INSERT INTO public.\w+_popularity_metrics.*?;",
            ddl,
            re.MULTILINE | re.DOTALL,
        )
    ):
        raise ValueError(f"Could not find insert statement in ddl file {ddl_filename}")

    for provider in metrics:
        assert provider in match.group(0)
