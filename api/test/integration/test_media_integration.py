"""This test suite covers common operations for all media types."""

import re

import pytest

from api.constants.licenses import LICENSE_GROUPS
from api.constants.parameters import COLLECTION, TAG
from test.fixtures.media_type_config import MediaTypeConfig


pytestmark = pytest.mark.django_db


def _check_non_es_fields_are_present(results: list[dict]):
    for result in results:
        # ``license`` is stored in ES, ``license_version`` is not.
        assert result["license_version"] is not None
        # ``creator`` is stored in ES, ``creator_url`` is not.
        assert result["creator_url"] is not None
        # ``foreign_landing_url`` is not stored in ES.
        assert result["foreign_landing_url"] is not None


@pytest.fixture
def search_results(
    media_type_config: MediaTypeConfig, api_client
) -> tuple[MediaTypeConfig, dict]:
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/", {"q": media_type_config.q}
    )
    assert res.status_code == 200

    data = res.json()
    return media_type_config, data


@pytest.fixture
def single_result(search_results) -> tuple[MediaTypeConfig, dict]:
    media_type_config, data = search_results
    item = data["results"][0]
    return media_type_config, item


@pytest.fixture
def related_results(single_result, api_client) -> tuple[MediaTypeConfig, dict, dict]:
    media_type_config, item = single_result
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{item['id']}/related/")
    assert res.status_code == 200

    data = res.json()
    return media_type_config, item, data


@pytest.fixture
def sensitive_result(
    media_type_config: MediaTypeConfig, api_client
) -> tuple[MediaTypeConfig, dict]:
    q = "bird"  # Not using the default ``q`` from ``media_type_config``.
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {"q": q, "unstable__include_sensitive_results": True},
    )
    assert res.status_code == 200

    data = res.json()
    # Raises ``StopIteration`` if no sensitive results are found.
    sensitive_result = next(
        result for result in data["results"] if result["unstable__sensitivity"]
    )

    return media_type_config, sensitive_result


##############
# Stats view #
##############


def test_stats(media_type_config: MediaTypeConfig, api_client):
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/stats/")
    data = res.json()
    num_media = 0
    provider_count = 0
    for pair in data:
        num_media += pair["media_count"]
        provider_count += 1
    assert num_media > 0
    assert provider_count > 0


###############
# Search view #
###############


def test_search_returns_non_zero_results(search_results):
    _, data = search_results
    assert data["result_count"] > 0


def test_search_handles_unbalanced_quotes_with_ok(
    media_type_config: MediaTypeConfig, api_client
):
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/", {"q": f'"{media_type_config.q}'}
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0


def test_search_handles_special_chars_with_ok(
    media_type_config: MediaTypeConfig, api_client
):
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/", {"q": f"{media_type_config.q}!"}
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0


def test_search_results_have_non_es_fields(search_results):
    _, data = search_results
    _check_non_es_fields_are_present(data["results"])


def test_search_removes_dupes_from_initial_pages(
    media_type_config: MediaTypeConfig, api_client
):
    """
    Return consistent, non-duplicate results in the first n pages.

    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages. This test ensures that no duplicates
    appear in the first few pages of a search query.
    """

    num_pages = 5

    searches = {
        api_client.get(f"/v1/{media_type_config.url_prefix}/", {"page": page})
        for page in range(1, num_pages)
    }

    results = set()
    for res in searches:
        parsed = res.json()
        for result in parsed["results"]:
            media_id = result["id"]
            assert media_id not in results  # Ensure that each result is new.
            results.add(media_id)


@pytest.mark.parametrize(
    "search_field, match_field", [("q", "title"), ("creator", "creator")]
)
def test_search_quotes_matches_only_exact(
    media_type_config: MediaTypeConfig, search_field, match_field, api_client
):
    # We want a query containing more than one word.
    if match_field == "title":
        q = "dancing penguins"
    else:
        q = (
            "The League"
            if media_type_config.media_type == "audio"
            else "Steve Wedgwood"
        )

    base_params = {"unstable__include_sensitive_results": True}
    path = f"/v1/{media_type_config.url_prefix}/"

    unquoted_res = api_client.get(path, base_params | {search_field: q})
    assert unquoted_res.status_code == 200

    unquoted_data = unquoted_res.json()
    unquoted_result_count = unquoted_data["result_count"]
    assert unquoted_result_count > 0

    unquoted_results = unquoted_data["results"]
    exact_matches = [q in item[match_field] for item in unquoted_results].count(True)
    assert 0 < exact_matches < unquoted_result_count

    quoted_res = api_client.get(path, base_params | {search_field: f'"{q}"'})
    assert quoted_res.status_code == 200

    quoted_data = quoted_res.json()
    quoted_result_count = quoted_data["result_count"]
    assert quoted_result_count > 0

    quoted_results = quoted_data["results"]
    assert all([q in item[match_field] for item in quoted_results])

    # Unquoted results will match more records due to the query being overall
    # less strict. Above we check that the results are not 0 to confirm that we
    # do still get results back.
    assert quoted_result_count < unquoted_result_count


def test_search_filters_by_source(media_type_config: MediaTypeConfig, api_client):
    provider = media_type_config.providers[0]
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {"q": media_type_config.q, "source": provider},
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["source"] == provider for result in data["results"])


def test_search_returns_zero_results_when_all_excluded(
    media_type_config: MediaTypeConfig, api_client
):
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {
            "q": media_type_config.q,
            "excluded_source": ",".join(media_type_config.providers),
        },
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] == 0


def test_search_refuses_both_sources_and_excluded(
    media_type_config: MediaTypeConfig, api_client
):
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {"q": media_type_config.q, "source": "x", "excluded_source": "y"},
    )
    assert res.status_code == 400


@pytest.mark.parametrize(
    "filter_rule, exp_licenses",
    [
        ({"license_type": "commercial"}, LICENSE_GROUPS["commercial"]),  # license group
        (
            {"license_type": "commercial,modification"},
            LICENSE_GROUPS["commercial"] & LICENSE_GROUPS["modification"],
        ),  # multiple license groups
        ({"license": "by"}, ["by"]),  # exact license
        ({"license": "by,by-nc-nd"}, ["by", "by-nc-nd"]),  # multiple exact licenses
        ({"license": "bY"}, ["by"]),  # case insensitive
    ],
)
def test_search_filters_by_license(
    media_type_config: MediaTypeConfig, filter_rule, exp_licenses, api_client
):
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/", filter_rule)
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["license"] in exp_licenses for result in data["results"])


def test_search_filters_by_extension(media_type_config: MediaTypeConfig, api_client):
    ext = "mp3" if media_type_config.media_type == "audio" else "jpg"
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/", {"extension": ext})
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["filetype"] == ext for result in data["results"])


def test_search_filters_by_category(media_type_config: MediaTypeConfig, api_client):
    for category in media_type_config.categories:
        res = api_client.get(
            f"/v1/{media_type_config.url_prefix}/", {"category": category}
        )
        assert res.status_code == 200

        data = res.json()
        assert data["result_count"] > 0
        assert all(result["category"] == category for result in data["results"])


def test_search_refuses_invalid_categories(
    media_type_config: MediaTypeConfig, api_client
):
    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/", {"category": "invalid_category"}
    )
    assert res.status_code == 400


################
# Detail view #
################


@pytest.mark.parametrize(
    "bad_uuid",
    [
        "000000000000000000000000000000000000",
        "123456789123456789123456789123456789",
        "12345678-1234-5678-1234-1234567891234",
        "abcd",
    ],
)
def test_detail_view_for_invalid_uuids_returns_not_found(
    media_type_config: MediaTypeConfig, bad_uuid: str, api_client
):
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{bad_uuid}/")
    assert res.status_code == 404


def test_search_with_only_valid_sources_produces_no_warning(
    media_type_config, api_client
):
    search = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {"source": ",".join(media_type_config.providers)},
    )
    assert search.status_code == 200
    assert "warnings" not in search.json()


def test_search_with_partially_invalid_sources_produces_warning_but_still_succeeds(
    media_type_config: MediaTypeConfig, api_client
):
    invalid_sources = [
        "surely_neither_this_one",
        "this_is_sure_not_to_ever_be_a_real_source_name",
    ]

    search = api_client.get(
        f"/v1/{media_type_config.url_prefix}/",
        {"source": ",".join([media_type_config.providers[0]] + invalid_sources)},
    )
    assert search.status_code == 200
    result = search.json()

    assert {w["code"] for w in result["warnings"]} == {
        "partially invalid source parameter"
    }
    warning = result["warnings"][0]
    assert set(warning["invalid_sources"]) == set(invalid_sources)
    assert warning["valid_sources"] == [media_type_config.providers[0]]
    assert f"v1/{media_type_config.url_prefix}/stats/" in warning["message"]


def test_search_with_all_invalid_sources_fails(media_type_config, api_client):
    invalid_sources = [
        "this_is_sure_not_to_ever_be_a_real_source_name",
        "surely_neither_this_one",
    ]
    search = api_client.get(
        f"/v1/{media_type_config.url_prefix}/", {"source": ",".join(invalid_sources)}
    )
    assert search.status_code == 400


def test_detail_view_returns_ok(single_result, api_client):
    media_type_config, item = single_result
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{item['id']}/")
    assert res.status_code == 200


def test_detail_view_contains_sensitivity_info(sensitive_result, api_client):
    media_type_config, item = sensitive_result
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{item['id']}/")
    assert res.status_code == 200

    data = res.json()
    assert data["unstable__sensitivity"] is not None
    assert len(data["unstable__sensitivity"]) > 0


################
# Related view #
################


@pytest.mark.parametrize(
    "bad_uuid",
    [
        "000000000000000000000000000000000000",
        "123456789123456789123456789123456789",
        "12345678-1234-5678-1234-1234567891234",
        "abcd",
    ],
)
def test_related_view_for_invalid_uuids_returns_not_found(
    media_type_config: MediaTypeConfig, bad_uuid: str, api_client
):
    res = api_client.get(f"/v1/{media_type_config.url_prefix}/{bad_uuid}/related/")
    assert res.status_code == 404


def test_related_view_has_no_pagination(related_results):
    _, _, data = related_results
    results = data["results"]
    assert data["result_count"] == len(results) == 10
    assert data["page_count"] == 1


def test_related_results_have_something_in_common_with_parent(related_results):
    _, item, data = related_results

    def _get_terms_set(obj):
        # The title is analyzed in ES, we try to mimic it here.
        terms = [t["name"] for t in obj["tags"]] + re.split(r"[\s-]", obj["title"])
        return {t.lower() for t in terms}

    terms_set = _get_terms_set(item)
    # Make sure each result has at least one word in common with the original item,
    # or is by the same creator.
    for result in data["results"]:
        assert (
            len(terms_set.intersection(_get_terms_set(result))) > 0
            or result["creator"] == item["creator"]
        ), f"{terms_set} {_get_terms_set(result)}/{result['creator']}-{item['creator']}"


def test_related_results_have_non_es_fields(related_results):
    *_, data = related_results
    _check_non_es_fields_are_present(data["results"])


###############
# Report view #
###############


def test_report_is_created(single_result, api_client):
    media_type_config, item = single_result
    res = api_client.post(
        f"/v1/{media_type_config.url_prefix}/{item['id']}/report/",
        {
            "reason": "mature",
            "description": "This item contains sensitive content",
        },
        "json",
    )
    assert res.status_code == 201

    data = res.json()
    assert data["identifier"] == item["id"]


####################
# Collection results #
####################


def test_collection_by_tag(media_type_config: MediaTypeConfig, api_client):
    tags = media_type_config.tags
    for tag in tags:
        res = api_client.get(
            f"/v1/{media_type_config.url_prefix}/?{COLLECTION}=tag&{TAG}={tag}"
        )
        assert res.status_code == 200

        data = res.json()
        assert data["result_count"] > 0
        for result in data["results"]:
            tag_names = [tag["name"] for tag in result["tags"]]
            assert tag in tag_names


def test_collection_by_source(media_type_config: MediaTypeConfig, api_client):
    source = api_client.get(f"/v1/{media_type_config.url_prefix}/stats/").json()[0][
        "source_name"
    ]

    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/?{COLLECTION}=source&source={source}"
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["source"] == source for result in data["results"])


def test_collection_by_creator(media_type_config: MediaTypeConfig, api_client):
    source_res = api_client.get(f"/v1/{media_type_config.url_prefix}/stats/")
    source = source_res.json()[0]["source_name"]

    first_res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/?{COLLECTION}=source&source={source}"
    )
    first = first_res.json()["results"][0]
    assert (creator := first.get("creator"))

    res = api_client.get(
        f"/v1/{media_type_config.url_prefix}/?{COLLECTION}=creator&source={source}&creator={creator}"
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    for result in data["results"]:
        assert result["source"] == source
        assert result["creator"] == creator
