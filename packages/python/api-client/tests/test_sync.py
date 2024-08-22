from openverse_api_client import OpenverseClient


def test_image_stats():
    client = OpenverseClient(base_url="http://localhost:50280")

    stats = client.request(client.endpoints["GET /v1/images/stats/"]())

    assert "flickr" in [s["source_name"] for s in stats.body]


def test_thumbnail():
    client = OpenverseClient(base_url="http://localhost:50280")

    image_search = client.request(client.endpoints["GET /v1/images/"](q="dogs"))

    image = image_search.body["results"][0]

    thumbnail = client.request(
        client.endpoints["GET /v1/images/{identifier}/thumb/"](image["id"])
    )
    assert isinstance(thumbnail.body, bytes)
