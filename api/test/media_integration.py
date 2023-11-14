"""
Base test cases for all media types.

These are not tests and cannot be invoked.
"""

import json
import re
from test.constants import API_URL

import requests


def search(fixture):
    """Return results for test query."""

    assert fixture["result_count"] > 0


def search_by_category(media_path, category, fixture):
    response = requests.get(f"{API_URL}/v1/{media_path}?category={category}")
    assert response.status_code == 200
    data = json.loads(response.text)
    assert data["result_count"] < fixture["result_count"]
    results = data["results"]
    # Make sure each result is from the specified category
    assert all(audio_item["category"] == category for audio_item in results)


def tag_collection(media_path):
    response = requests.get(f"{API_URL}/v1/{media_path}/tag/cat")
    assert response.status_code == 200

    results = response.json()["results"]
    for r in results:
        tag_names = [tag["name"] for tag in r["tags"]]
        assert "cat" in tag_names


def source_collection(media_path):
    source = requests.get(f"{API_URL}/v1/{media_path}/stats").json()[0]["source_name"]

    response = requests.get(f"{API_URL}/v1/{media_path}/source/{source}")
    assert response.status_code == 200

    results = response.json()["results"]
    assert all(result["source"] == source for result in results)


def creator_collection(media_path):
    source = requests.get(f"{API_URL}/v1/{media_path}/stats").json()[0]["source_name"]

    first_res = requests.get(f"{API_URL}/v1/{media_path}/source/{source}").json()[
        "results"
    ][0]
    if not (creator := first_res.get("creator")):
        raise AttributeError(f"No creator in {first_res}")

    response = requests.get(
        f"{API_URL}/v1/{media_path}/source/{source}/creator/{creator}"
    )
    assert response.status_code == 200

    results = response.json()["results"]
    assert all(
        r["creator"] == "creator" and results["source"] == source for r in results
    )


def search_all_excluded(media_path, excluded_source):
    response = requests.get(
        f"{API_URL}/v1/{media_path}?q=test&excluded_source={','.join(excluded_source)}"
    )
    data = json.loads(response.text)
    assert data["result_count"] == 0


def search_source_and_excluded(media_path):
    response = requests.get(
        f"{API_URL}/v1/{media_path}?q=test&source=x&excluded_source=y"
    )
    assert response.status_code == 400


def search_quotes(media_path, q="test"):
    """Return a response when quote matching is messed up."""

    response = requests.get(f'{API_URL}/v1/{media_path}?q="{q}', verify=False)
    assert response.status_code == 200


def search_quotes_exact(media_path, q):
    """Return only exact matches for the given query."""

    url_format = f"{API_URL}/v1/{media_path}?q={{q}}"
    unquoted_response = requests.get(url_format.format(q=q), verify=False)
    assert unquoted_response.status_code == 200
    unquoted_result_count = unquoted_response.json()["result_count"]
    assert unquoted_result_count > 0

    quoted_response = requests.get(url_format.format(q=f'"{q}"'), verify=False)
    assert quoted_response.status_code == 200
    quoted_result_count = quoted_response.json()["result_count"]
    assert quoted_result_count > 0

    # The rationale here is that the unquoted results will match more records due
    # to the query being overall less strict. Quoting the query will make it more
    # strict causing it to return fewer results.
    # Above we check that the results are not 0 to confirm that we do still get results back.
    assert quoted_result_count < unquoted_result_count


def search_special_chars(media_path, q="test"):
    """Return a response when query includes special characters."""

    response = requests.get(f"{API_URL}/v1/{media_path}?q={q}!", verify=False)
    assert response.status_code == 200


def search_consistency(
    media_path,
    n_pages,
):
    """
    Return consistent, non-duplicate results in the first n pages.

    Elasticsearch sometimes reaches an inconsistent state, which causes search
    results to appear differently upon page refresh. This can also introduce
    image duplicates in subsequent pages. This test ensures that no duplicates
    appear in the first few pages of a search query.
    """

    searches = {
        requests.get(f"{API_URL}/v1/{media_path}?page={page}", verify=False)
        for page in range(1, n_pages)
    }

    results = set()
    for response in searches:
        parsed = json.loads(response.text)
        for result in parsed["results"]:
            media_id = result["id"]
            assert media_id not in results
            results.add(media_id)


def detail(media_type, fixture):
    test_id = fixture["results"][0]["id"]
    response = requests.get(f"{API_URL}/v1/{media_type}/{test_id}", verify=False)
    assert response.status_code == 200


def stats(media_type, count_key="media_count"):
    response = requests.get(f"{API_URL}/v1/{media_type}/stats", verify=False)
    parsed_response = json.loads(response.text)
    assert response.status_code == 200
    num_media = 0
    provider_count = 0
    for pair in parsed_response:
        media_count = pair[count_key]
        num_media += int(media_count)
        provider_count += 1
    assert num_media > 0
    assert provider_count > 0


def report(media_type, fixture):
    test_id = fixture["results"][0]["id"]
    response = requests.post(
        f"{API_URL}/v1/{media_type}/{test_id}/report/",
        json={
            "reason": "mature",
            "description": "This item contains sensitive content",
        },
        verify=False,
    )
    assert response.status_code == 201
    data = json.loads(response.text)
    assert data["identifier"] == test_id


def license_filter_case_insensitivity(media_type):
    response = requests.get(f"{API_URL}/v1/{media_type}?license=bY", verify=False)
    parsed = json.loads(response.text)
    assert parsed["result_count"] > 0


def uuid_validation(media_type, identifier):
    response = requests.get(f"{API_URL}/v1/{media_type}/{identifier}", verify=False)
    assert response.status_code == 404


def related(fixture):
    item = fixture["results"][0]

    response = requests.get(item["related_url"]).json()
    results = response["results"]

    assert response["result_count"] == len(results) == 10
    assert response["page_count"] == 1

    def get_terms_set(res):
        # The title is analyzed in ES, we try to mimic it here.
        terms = [t["name"] for t in res["tags"]] + re.split(" |-", res["title"])
        return {t.lower() for t in terms}

    terms_set = get_terms_set(item)
    # Make sure each result has at least one word in common with the original item,
    # or is by the same creator.
    for result in results:
        assert (
            len(terms_set.intersection(get_terms_set(result))) > 0
            or result["creator"] == item["creator"]
        ), f"{terms_set} {get_terms_set(result)}/{result['creator']}-{item['creator']}"


def sensitive_search_and_detail(media_type):
    search_res = requests.get(
        f"{API_URL}/v1/{media_type}/",
        params={"q": "bird", "unstable__include_sensitive_results": "true"},
        verify=False,
    )
    results = search_res.json()["results"]

    sensitive_result = None
    sensitivities = []
    for result in results:
        if sensitivities := result["unstable__sensitivity"]:
            sensitive_result = result
            break
    assert sensitive_result is not None
    assert len(sensitivities) != 0

    detail_res = requests.get(
        f"{API_URL}/v1/{media_type}/{sensitive_result['id']}", verify=False
    )
    details = detail_res.json()

    assert sensitivities == details["unstable__sensitivity"]
