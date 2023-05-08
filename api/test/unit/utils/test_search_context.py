import pytest

from api.utils.search_context import SearchContext


pytestmark = pytest.mark.django_db


def test_no_results(origin_index):
    search_context = SearchContext.build([], origin_index)

    assert search_context == SearchContext(set(), set(), set())


def test_clear_result(origin_index, model_factory):
    media = model_factory.create(mature_reported=False)
    model_factory.save_model_to_es(
        media,
        # Include in the filtered index to represent
        # a document without sensitive terms
        filtered=True,
        mature=False,
    )
    results = [model_factory.create_hit(media)]

    search_context = SearchContext.build(results, origin_index)

    assert search_context == SearchContext(
        {r.identifier for r in results},
        set(),
        set(),
    )


parametrize_filtered = pytest.mark.parametrize(
    "filtered",
    (True, False),
    ids=lambda x: "no_sensitive_text" if x else "sensitive_text",
)


@parametrize_filtered
def test_user_reported_mature_result(origin_index, model_factory, filtered):
    media = model_factory.create(mature_reported=True)
    model_factory.save_model_to_es(
        media,
        filtered=filtered,
    )
    results = [model_factory.create_hit(media)]

    search_context = SearchContext.build(results, origin_index)

    identifiers = {r.identifier for r in results}

    assert search_context == SearchContext(
        all_result_identifiers=identifiers,
        user_reported_sensitive_result_identifiers=identifiers,
        sensitive_text_result_identifiers=identifiers if not filtered else set(),
    )


@parametrize_filtered
def test_provider_mature_result(origin_index, model_factory, filtered):
    media = model_factory.create(mature_reported=False)
    model_factory.save_model_to_es(
        media,
        filtered=filtered,
        mature=True,
    )
    results = [model_factory.create_hit(media)]

    search_context = SearchContext.build(results, origin_index)

    identifiers = {r.identifier for r in results}

    assert search_context == SearchContext(
        all_result_identifiers=identifiers,
        user_reported_sensitive_result_identifiers=set(),
        sensitive_text_result_identifiers=identifiers if not filtered else set(),
    )
