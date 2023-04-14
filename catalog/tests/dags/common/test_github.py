import pook
import pytest
from requests import HTTPError

from common.github import GitHubAPI


SAMPLE_PAT = "foobar"


@pytest.fixture
def github():
    return GitHubAPI(pat=SAMPLE_PAT)


@pytest.mark.parametrize(
    "method, resource, status_code, response_text, expected",
    [
        # Standard replies
        ("get", "repos/WordPress/openverse/pulls", 200, "[]", []),
        (
            "put",
            "repos/WordPress/openverse/pull",
            200,
            '{"key":"value","a":2}',
            {"key": "value", "a": 2},
        ),
        # 204 No Content reply
        ("delete", "repos/WordPress/openverse/comment/555", 204, "", None),
        # Failure replies
        pytest.param(
            "get",
            "repos/WordPress/openverse/pulls",
            400,
            "[]",
            [],
            marks=pytest.mark.raises(exception=HTTPError),
        ),
        pytest.param(
            "get",
            "repos/WordPress/openverse/pulls",
            500,
            "[]",
            [],
            marks=pytest.mark.raises(exception=HTTPError),
        ),
    ],
)
@pook.on
def test_github_make_request(
    method, resource, status_code, response_text, expected, github
):
    pook_func = getattr(pook, method.lower())
    pook_func(f"https://api.github.com/{resource}").reply(status_code).body(
        response_text
    )
    assert github._make_request(method, resource) == expected
