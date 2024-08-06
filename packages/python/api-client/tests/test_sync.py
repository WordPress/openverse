from openverse_api_client import OpenverseClient


def test_image_stats():
    client = OpenverseClient(base_url="http://localhost:50280")

    stats = client.v1_image_stats()

    assert "flickr" in [s["source_name"] for s in stats.body]


def test_thumbnail():
    client = OpenverseClient(base_url="http://localhost:50280")

    image_search = client.v1_image_search(q="dogs")

    image = image_search.body["results"][0]

    thumbnail = client.v1_image_thumb(image["id"])
    assert isinstance(thumbnail.body, bytes)
