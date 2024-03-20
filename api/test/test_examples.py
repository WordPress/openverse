import json
import os
import subprocess

from django.conf import settings

import pytest


os.environ["REQUEST_TOKEN"] = ""
os.environ["CANONICAL_DOMAIN"] = settings.CANONICAL_DOMAIN

from api.examples import (  # noqa: E402 | Set env vars before import
    audio_mappings,
    image_mappings,
)


def execute_request(request):
    try:
        proc = subprocess.run(request, check=True, capture_output=True, shell=True)
        return json.loads(proc.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise


@pytest.mark.parametrize("in_val, out_val", list(audio_mappings.items()))
def test_audio_success_examples(in_val, out_val):
    res = execute_request(in_val)
    assert res == out_val["application/json"]


@pytest.mark.parametrize("in_val, out_val", list(image_mappings.items()))
def test_image_success_examples(in_val, out_val):
    res = execute_request(in_val)
    assert res == out_val["application/json"]
