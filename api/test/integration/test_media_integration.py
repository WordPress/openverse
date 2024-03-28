"""This test suite covers common operations for all media types."""

import re
from dataclasses import dataclass

import pytest

from api.constants.licenses import LICENSE_GROUPS
from api.constants.parameters import COLLECTION, TAG


pytestmark = pytest.mark.django_db


@dataclass
class MediaType:
    name: str  # the name of the media type
    path: str  # the version of the media type in the URL paths
    providers: list[str]  # providers for the media type from the sample data
    categories: list[str]  # categories for the media type from the sample data
    tags: list[str]  # tags for the media type from the sample data
    q: str  # a search query for this media type that yields some results


def _check_non_es_fields_are_present(results: list[dict]):
    for result in results:
        # ``license`` is stored in ES, ``license_version`` is not.
        assert result["license_version"] is not None
        # ``creator`` is stored in ES, ``creator_url`` is not.
        assert result["creator_url"] is not None
        # ``foreign_landing_url`` is not stored in ES.
        assert result["foreign_landing_url"] is not None


############
# Fixtures #
############


@pytest.fixture(params=["audio", "image"])
def media_type(request):
    """
    Get a ``MediaType`` object associated with each media type supported by
    Openverse. This fixture is used to parametrize tests and other dependent
    fixtures so that the overall test suite covers all supported media types.
    """

    name = request.param
    return {
        "audio": MediaType(
            name="audio",
            path="audio",
            providers=["freesound", "jamendo", "wikimedia_audio", "ccmixter"],
            categories=["music", "pronunciation"],
            tags=["cat"],
            q="love",
        ),
        "image": MediaType(
            name="image",
            path="images",
            providers=["flickr", "stocksnap"],
            categories=["photograph"],
            tags=["cat", "Cat"],
            q="dog",
        ),
    }[name]


@pytest.fixture
def search_results(media_type: MediaType, api_client) -> tuple[MediaType, dict]:
    res = api_client.get(f"/v1/{media_type.path}/", {"q": media_type.q})
    assert res.status_code == 200

    data = res.json()
    return media_type, data


@pytest.fixture
def single_result(search_results) -> tuple[MediaType, dict]:
    media_type, data = search_results
    item = data["results"][0]
    return media_type, item


@pytest.fixture
def related_results(single_result, api_client) -> tuple[MediaType, dict, dict]:
    media_type, item = single_result
    res = api_client.get(f"/v1/{media_type.path}/{item['id']}/related/")
    assert res.status_code == 200

    data = res.json()
    return media_type, item, data


@pytest.fixture
def sensitive_result(media_type: MediaType, api_client) -> tuple[MediaType, dict]:
    q = "bird"  # Not using the default ``q`` from ``media_type``.
    res = api_client.get(
        f"/v1/{media_type.path}/",
        {"q": q, "unstable__include_sensitive_results": True},
    )
    assert res.status_code == 200

    data = res.json()
    # Raises ``StopIteration`` if no sensitive results are found.
    sensitive_result = next(
        result for result in data["results"] if result["unstable__sensitivity"]
    )

    return media_type, sensitive_result


##############
# Stats view #
##############


def test_stats(media_type: MediaType, api_client):
    res = api_client.get(f"/v1/{media_type.path}/stats/")
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


def test_search_handles_unbalanced_quotes_with_ok(media_type: MediaType, api_client):
    res = api_client.get(f"/v1/{media_type.path}/", {"q": f'"{media_type.q}'})
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0


def test_search_handles_special_chars_with_ok(media_type: MediaType, api_client):
    res = api_client.get(f"/v1/{media_type.path}/", {"q": f"{media_type.q}!"})
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0


def test_search_results_have_non_es_fields(search_results):
    _, data = search_results
    _check_non_es_fields_are_present(data["results"])


def test_search_removes_dupes_from_initial_pages(media_type: MediaType, api_client):
    """
    Return consistent, non-duplicate results in the first n pages.

    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages. This test ensures that no duplicates
    appear in the first few pages of a search query.
    """

    num_pages = 5

    searches = {
        api_client.get(f"/v1/{media_type.path}/", {"page": page})
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
    media_type: MediaType, search_field, match_field, api_client
):
    # We want a query containing more than one word.
    if match_field == "title":
        q = "dancing penguins"
    else:
        q = "The League" if media_type.name == "audio" else "Steve Wedgwood"

    base_params = {"unstable__include_sensitive_results": True}
    path = f"/v1/{media_type.path}/"

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


def test_search_filters_by_source(media_type: MediaType, api_client):
    provider = media_type.providers[0]
    res = api_client.get(
        f"/v1/{media_type.path}/",
        {"q": media_type.q, "source": provider},
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["source"] == provider for result in data["results"])


def test_search_returns_zero_results_when_all_excluded(
    media_type: MediaType, api_client
):
    res = api_client.get(
        f"/v1/{media_type.path}/",
        {"q": media_type.q, "excluded_source": ",".join(media_type.providers)},
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] == 0


def test_search_refuses_both_sources_and_excluded(media_type: MediaType, api_client):
    res = api_client.get(
        f"/v1/{media_type.path}/",
        {"q": media_type.q, "source": "x", "excluded_source": "y"},
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
    media_type: MediaType, filter_rule, exp_licenses, api_client
):
    res = api_client.get(f"/v1/{media_type.path}/", filter_rule)
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["license"] in exp_licenses for result in data["results"])


def test_search_filters_by_extension(media_type: MediaType, api_client):
    ext = "mp3" if media_type.name == "audio" else "jpg"
    res = api_client.get(f"/v1/{media_type.path}/", {"extension": ext})
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["filetype"] == ext for result in data["results"])


def test_search_filters_by_category(media_type: MediaType, api_client):
    for category in media_type.categories:
        res = api_client.get(f"/v1/{media_type.path}/", {"category": category})
        assert res.status_code == 200

        data = res.json()
        assert data["result_count"] > 0
        assert all(result["category"] == category for result in data["results"])


def test_search_refuses_invalid_categories(media_type: MediaType, api_client):
    res = api_client.get(f"/v1/{media_type.path}/", {"category": "invalid_category"})
    assert res.status_code == 400


################
# Detail view #
################


@pytest.mark.parametrize(
    "bad_uuid",
    [
        "123456789123456789123456789123456789",
        "12345678-1234-5678-1234-1234567891234",
        "abcd",
    ],
)
def test_detail_view_for_invalid_uuids_returns_not_found(
    media_type: MediaType, bad_uuid: str, api_client
):
    res = api_client.get(f"/v1/{media_type.path}/{bad_uuid}/")
    assert res.status_code == 404


def test_detail_view_returns_ok(single_result, api_client):
    media_type, item = single_result
    res = api_client.get(f"/v1/{media_type.path}/{item['id']}/")
    assert res.status_code == 200


def test_detail_view_contains_sensitivity_info(sensitive_result, api_client):
    media_type, item = sensitive_result
    res = api_client.get(f"/v1/{media_type.path}/{item['id']}/")
    assert res.status_code == 200

    data = res.json()
    assert data["unstable__sensitivity"] is not None
    assert len(data["unstable__sensitivity"]) > 0


################
# Related view #
################


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
    media_type, item = single_result
    res = api_client.post(
        f"/v1/{media_type.path}/{item['id']}/report/",
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


def test_collection_by_tag(media_type: MediaType, api_client):
    tags = media_type.tags
    for tag in tags:
        res = api_client.get(f"/v1/{media_type.path}/?{COLLECTION}=tag&{TAG}={tag}")
        assert res.status_code == 200

        data = res.json()
        assert data["result_count"] > 0
        for result in data["results"]:
            tag_names = [tag["name"] for tag in result["tags"]]
            assert tag in tag_names


def test_collection_by_source(media_type: MediaType, api_client):
    source = api_client.get(f"/v1/{media_type.path}/stats/").json()[0]["source_name"]

    res = api_client.get(f"/v1/{media_type.path}/?{COLLECTION}=source&source={source}")
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    assert all(result["source"] == source for result in data["results"])


def test_collection_by_creator(media_type: MediaType, api_client):
    source_res = api_client.get(f"/v1/{media_type.path}/stats/")
    source = source_res.json()[0]["source_name"]

    first_res = api_client.get(
        f"/v1/{media_type.path}/?{COLLECTION}=source&source={source}"
    )
    first = first_res.json()["results"][0]
    assert (creator := first.get("creator"))

    res = api_client.get(
        f"/v1/{media_type.path}/?{COLLECTION}=creator&source={source}&creator={creator}"
    )
    assert res.status_code == 200

    data = res.json()
    assert data["result_count"] > 0
    for result in data["results"]:
        assert result["source"] == source
        assert result["creator"] == creator
