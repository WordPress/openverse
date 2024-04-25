from unittest import mock

from django.db.utils import OperationalError

import pook
import pytest


def mock_health_response(status="green", timed_out=False):
    return (
        pook.get(pook.regex(r"_cluster\/health"))
        .times(1)
        .reply(200)
        .json(
            {
                "status": status if not timed_out else None,
                "timed_out": timed_out,
            }
        )
    )


@pytest.mark.django_db
def test_health_check_plain(api_client):
    res = api_client.get("/healthcheck/")
    assert res.status_code == 200


def test_health_check_calls__check_db(api_client):
    with mock.patch("api.views.health_views.HealthCheck._check_db") as mock_check_db:
        res = api_client.get("/healthcheck/")
        assert res.status_code == 200
        mock_check_db.assert_called_once()


def test_health_check_calls__check_db_with_failure(api_client):
    with mock.patch(
        "api.views.health_views.connection.ensure_connection"
    ) as mock_ensure_connection:
        mock_ensure_connection.side_effect = OperationalError("Database has gone away")
        res = api_client.get("/healthcheck/")
        assert res.status_code == 503
        assert res.json() == {"detail": "Database unavailable: Database has gone away"}
        mock_ensure_connection.assert_called_once()


def test_health_check_es_timed_out(api_client):
    with pook.use():
        mock_health_response(timed_out=True)
        res = api_client.get("/healthcheck/", data={"check_es": True})

    assert res.status_code == 503
    assert res.json() == {"detail": "es_timed_out"}


@pytest.mark.parametrize("status", ("yellow", "red"))
def test_health_check_es_status_bad(status, api_client):
    with pook.use():
        mock_health_response(status=status)
        res = api_client.get("/healthcheck/", data={"check_es": True})

    assert res.status_code == 503
    assert res.json() == {"detail": f"es_status_{status}"}


@pytest.mark.django_db
def test_health_check_es_all_good(api_client):
    with pook.use():
        mock_health_response(status="green")
        res = api_client.get("/healthcheck/", data={"check_es": True})

    assert res.status_code == 200
