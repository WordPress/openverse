"""
End-to-end API tests for audio.

Tests common to all media types are in ``test_media_integration.py``.
"""

import os
import subprocess
from unittest import mock

import pook
import pytest


pytestmark = pytest.mark.django_db


def test_audio_detail_without_thumb(api_client):
    resp = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/")
    assert resp.status_code == 200
    parsed = resp.json()
    assert parsed["thumbnail"] is None


def test_audio_search_without_thumb(api_client):
    """The first audio of this search should not have a thumbnail."""
    resp = api_client.get("/v1/audio/?q=zaus")
    assert resp.status_code == 200
    parsed = resp.json()
    assert parsed["results"][0]["thumbnail"] is None


def test_audio_waveform(api_client):
    resp = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/waveform/")
    assert resp.status_code == 200
    parsed = resp.json()
    assert parsed["len"] == len(parsed["points"])


def test_audio_generation_failure(monkeypatch, api_client):
    mock_subprocess_run = mock.Mock()
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "", "", "")
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    resp = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/waveform/")
    assert resp.status_code == 424
    mock_subprocess_run.assert_called_once()
    assert "Could not generate the waveform." == resp.json()["detail"]


def test_audio_waveform_cleanup_failure_does_not_fail_request(monkeypatch, api_client):
    mock_os_remove = mock.Mock()
    mock_os_remove.side_effect = OSError("beep boop")
    monkeypatch.setattr(os, "remove", mock_os_remove)
    resp = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/waveform/")
    assert resp.status_code == 200
    mock_os_remove.assert_called_once()


@pytest.mark.pook(start_active=False)
def test_audio_waveform_upstream_failure(api_client):
    audio_res = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/")
    audio = audio_res.json()

    pook.on()
    pook.get(audio["url"]).reply(500)

    resp = api_client.get("/v1/audio/44540200-91eb-483d-9e99-38ce86a52fb6/waveform/")
    assert resp.status_code == 424
    assert "problem connecting to the provider" in resp.json()["detail"]
