import pytest

from api.utils.search_context import SearchContext


pytestmark = pytest.mark.django_db


def test_no_results(media_type_config):
    search_context = SearchContext.build([], media_type_config.origin_index)

    assert search_context == SearchContext(set(), set())


@pytest.mark.parametrize(
    "has_sensitive_text",
    (True, False),
    ids=lambda x: "has_sensitive_text" if x else "no_sensitive_text",
)
def test_sensitive_text(media_type_config, has_sensitive_text):
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

    search_context = SearchContext.build(results, media_type_config.origin_index)

    assert search_context == SearchContext(
        {r.identifier for r in results},
        {maybe_sensitive_text_model.identifier} if has_sensitive_text else set(),
    )
