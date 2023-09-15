import pook
import pytest

from api.utils.search_context import SearchContext


pytestmark = pytest.mark.django_db


def test_no_results(media_type_config):
    search_context = SearchContext.build([], media_type_config.origin_index)

    assert search_context == SearchContext(list(), set())


@pytest.mark.parametrize(
    "has_sensitive_text",
    (True, False),
    ids=lambda x: "has_sensitive_text" if x else "no_sensitive_text",
)
@pytest.mark.parametrize(
    "setting_enabled",
    (True, False),
    ids=lambda x: "setting_enabled" if x else "setting_disabled",
)
def test_sensitive_text(
    media_type_config, has_sensitive_text, setting_enabled, settings
):
    settings.ENABLE_FILTERED_INDEX_QUERIES = setting_enabled

    clear_results = media_type_config.model_factory.create_batch(
        # Use size 10 to force result size beyond the default ES query window
        size=10,
        mature_reported=False,
        provider_marked_mature=False,
        sensitive_text=False,
        with_hit=True,
    )

    (
        maybe_sensitive_text_model,
        maybe_sensitive_text_hit,
    ) = media_type_config.model_factory.create(
        mature_reported=False,
        provider_marked_mature=False,
        sensitive_text=has_sensitive_text,
        with_hit=True,
    )

    results = [maybe_sensitive_text_hit] + [hit for _, hit in clear_results]
    result_ids = [result.identifier for result in results]

    if not setting_enabled:
        with pook.post(
            f"{settings.ES_ENDPOINT}/{media_type_config.filtered_index}/_search",
            reply=500,
        ) as mock:
            search_context = SearchContext.build(
                result_ids, media_type_config.origin_index
            )
            assert (
                mock.total_matches == 0
            ), "There should be zero requests to ES if the setting is disabled"
        pook.off()
    else:
        search_context = SearchContext.build(result_ids, media_type_config.origin_index)

    assert search_context == SearchContext(
        [r.identifier for r in results],
        {maybe_sensitive_text_model.identifier}
        if has_sensitive_text and setting_enabled
        else set(),
    )
