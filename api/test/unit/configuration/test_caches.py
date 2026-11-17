import pytest

from conf.settings import caches


@pytest.mark.parametrize(
    "use_tls, password, expected_scheme, expected_password",
    (
        (False, "", "redis", None),
        (True, "", "rediss", None),
        (True, "example-token", "rediss", "example-token"),
    ),
)
def test_make_cache_config_applies_tls_and_password(
    monkeypatch, use_tls, password, expected_scheme, expected_password
):
    monkeypatch.setattr(caches, "REDIS_USE_TLS", use_tls)
    monkeypatch.setattr(caches, "REDIS_PASSWORD", password)

    config = caches._make_cache_config(3)

    assert config["LOCATION"].startswith(f"{expected_scheme}://")
    assert config["LOCATION"].endswith("/3")
    assert config["OPTIONS"].get("PASSWORD") == expected_password
