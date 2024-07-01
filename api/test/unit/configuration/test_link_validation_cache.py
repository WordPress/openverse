from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured

import pytest

from conf.settings.link_validation_cache import LinkValidationCacheExpiryConfiguration


@pytest.mark.parametrize(
    ("status", "td"),
    (
        (200, timedelta(days=30)),
        (-1, timedelta(minutes=30)),
        # subsequent entries all use default
        (400, timedelta(days=120)),
        (500, timedelta(days=120)),
        (503, timedelta(days=120)),
        (401, timedelta(days=120)),
        (301, timedelta(days=120)),
    ),
)
def test_all_default_values(status, td):
    config = LinkValidationCacheExpiryConfiguration()

    assert config[status] == int(td.total_seconds())


@pytest.mark.filterwarnings(
    # Due to expected exceptions raised by the tests
    "ignore:A plugin raised an exception during an old-style hookwrapper teardown"
)
@pytest.mark.parametrize(
    ("overrides", "expecteds"),
    (
        ({"default": '{"days": 1}'}, ((400, timedelta(days=1)),)),
        ({"200": '{"days": 3}'}, ((200, timedelta(days=3)),)),
        ({"200": '{"days": 3}'}, ((300, timedelta(days=120)),)),
        ({"-1": '{"seconds": 120}'}, ((-1, timedelta(seconds=120)),)),
        # invalid value
        pytest.param(
            {"default": "not parseable"},
            ((400, None),),
            marks=pytest.mark.raises(exception=ImproperlyConfigured),
        ),
        # invalid key
        pytest.param(
            {"3a312": '{"hours": 12}'},
            ((200, None),),
            marks=pytest.mark.raises(exception=ImproperlyConfigured),
        ),
        # invalid arguments for timedelta
        pytest.param(
            {"500": '{"not_a_valid_keyword": 12}'},
            ((200, None),),
            marks=pytest.mark.raises(exception=ImproperlyConfigured),
        ),
        # multiple configurations
        (
            {
                "default": '{"minutes": 25}',
                "500": '{"days": 20}',
                "200": '{"days": 1}',
            },
            (
                (324, timedelta(minutes=25)),
                (500, timedelta(days=20)),
                (200, timedelta(days=1)),
                (400, timedelta(minutes=25)),
                # -1 still retains default value, doesn't use the `default` override
                (-1, timedelta(minutes=30)),
            ),
        ),
    ),
)
def test_environment_overrides(overrides, expecteds, monkeypatch):
    for k, v in overrides.items():
        env_key = f"{LinkValidationCacheExpiryConfiguration.SETTING_PREFIX}{k}"
        monkeypatch.setenv(env_key, v)

    config = LinkValidationCacheExpiryConfiguration()

    for status, td in expecteds:
        assert config[status] == td.total_seconds()
