import pytest
from openverse_api_client import AsyncOpenverseClient


pytestmark = [
    pytest.mark.asyncio,
]


async def test_image_stats():
    client = AsyncOpenverseClient(base_url="http://localhost:50280")
    stats = await client.request(client.endpoint("GET /v1/images/stats/")())

    assert "flickr" in [s["source_name"] for s in stats.body]


async def test_thumbnail():
    client = AsyncOpenverseClient(base_url="http://localhost:50280")
    image_search = await client.request(client.endpoint("GET /v1/images/")(q="dogs"))

    image = image_search.body["results"][0]

    thumbnail = await client.request(
        client.endpoint("GET /v1/images/{identifier}/thumb/")(image["id"])
    )
    assert isinstance(thumbnail.body, bytes)
