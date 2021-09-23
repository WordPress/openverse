import json
import os
import subprocess
from test.constants import API_URL

import pytest


os.environ["AUDIO_REQ_TOKEN"] = ""
os.environ["AUDIO_REQ_ORIGIN"] = API_URL
os.environ["AUDIO_REQ_IDX"] = "440a0240-8b20-49e2-a4e6-6fee550fcc41"

from catalog.api.examples import (  # noqa | Set env vars before import
    audio_mappings,
    image_mappings,
)


def execute_request(request):
    proc = subprocess.run(request, check=True, capture_output=True, shell=True)
    return json.loads(proc.stdout)


@pytest.mark.parametrize("in_val, out_val", list(audio_mappings.items()))
def test_audio_success_examples(in_val, out_val):
    res = execute_request(in_val)
    assert res == out_val["application/json"]


@pytest.mark.parametrize("in_val, out_val", list(image_mappings.items()))
def test_image_success_examples(in_val, out_val):
    res = execute_request(in_val)
    assert res == out_val["application/json"]
