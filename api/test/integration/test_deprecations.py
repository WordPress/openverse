import uuid

import pytest


@pytest.mark.parametrize(
    "old, new",
    [
        ("/v1/sources?type=images", "/v1/images/stats/"),
        ("/v1/recommendations/images/{idx}", "/v1/images/{idx}/related/"),
        ("/v1/oembed?key=value", "/v1/images/oembed/?key=value"),
        ("/v1/thumbs/{idx}", "/v1/images/{idx}/thumb/"),
    ],
)
def test_deprecated_endpoints_redirect_to_new(old, new, client):
    idx = uuid.uuid4()
    old = old.format(idx=str(idx))
    new = new.format(idx=str(idx))

    res = client.get(old)
    assert res.status_code == 301
    assert res.headers.get("Location") == new
