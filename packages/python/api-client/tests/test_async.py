import pytest
from openverse_api_client import AsyncOpenverseClient


pytestmark = [
    pytest.mark.asyncio,
]


async def test_image_stats():
    client = AsyncOpenverseClient(base_url="http://localhost:50280")
    request = client.endpoints["GET /v1/images/stats/"]()
    stats = await client(request)

    assert "flickr" in [s["source_name"] for s in stats.body]


async def test_image_stats_non_instance():
    client = AsyncOpenverseClient(base_url="http://localhost:50280")
    request = client.endpoints["GET /v1/images/stats/"]
    stats = await client(request)

    assert "flickr" in [s["source_name"] for s in stats.body]


async def test_thumbnail():
    client = AsyncOpenverseClient(base_url="http://localhost:50280")
    request = client.endpoints["GET /v1/images/"](q="dogs")
    image_search = await client(request)

    image = image_search.body["results"][0]

    thumbnail_request = client.endpoints["GET /v1/images/{identifier}/thumb/"](
        image["id"]
    )
    thumbnail = await client(thumbnail_request)
    assert isinstance(thumbnail.body, bytes)
