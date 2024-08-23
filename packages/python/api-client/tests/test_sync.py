from openverse_api_client import OpenverseClient


def test_image_stats():
    client = OpenverseClient(base_url="http://localhost:50280")

    req = client.endpoints["GET /v1/images/stats/"]()
    stats = client(req)

    assert "flickr" in [s["source_name"] for s in stats.body]


def test_image_stats_no_param():
    client = OpenverseClient(base_url="http://localhost:50280")

    req = client.endpoints["GET /v1/images/stats/"]
    stats = client(req)

    assert "flickr" in [s["source_name"] for s in stats.body]


def test_thumbnail():
    client = OpenverseClient(base_url="http://localhost:50280")

    image_search_request = client.endpoints["GET /v1/images/"](q="dogs")
    image_search = client(image_search_request)

    image = image_search.body["results"][0]

    thumbnail_request = client.endpoints["GET /v1/images/{identifier}/thumb/"](
        image["id"]
    )
    thumbnail = client(thumbnail_request)
    assert isinstance(thumbnail.body, bytes)
