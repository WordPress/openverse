from api.examples.environment import ORIGIN, TOKEN


auth = f'-H "Authorization: Bearer {TOKEN}"' if TOKEN else ""
identifier = "4bc43a04-ef46-4544-a0c1-63c63f56e276"

syntax_examples = {
    "using single query parameter": "test",
    "using multiple query parameters": "test&license=pdm,by&categories=illustration&page_size=1&page=1",  # noqa: E501
    "that are an exact match of Claude Monet": "%22Claude%20Monet%22",
    "related to both dog and cat": "dog+cat",
    "related to dog or cat, but not necessarily both": "dog|cat",
    "related to dog but won't include results related to 'pug'": "dog -pug",
    "matching anything with the prefix ‘net’": "net*",
    "matching dogs that are either corgis or labrador": "dogs + (corgis | labrador)",
    "matching strings close to the term theater"
    "with a difference of one character": "theatre~1",
}

image_search_list_curl = "\n".join(
    f"""
# Example {index}: Search for images {purpose}
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/?q={syntax}"
"""
    for (index, (purpose, syntax)) in enumerate(syntax_examples.items())
)

image_search_curl = f"""
# Search for images titled "Bark" by Sullivan
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/?title=Bark&creator=Sullivan"
"""

image_stats_curl = f"""
# Get the statistics for image sources
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/stats/"
"""

image_detail_curl = f"""
# Get the details of image ID {identifier}
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/{identifier}/"
"""

image_related_curl = f"""
# Get related images for image ID {identifier}
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/{identifier}/related/"
"""

image_complain_curl = f"""
# Report an issue about image ID {identifier}
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  {auth} \\
  -d '{{"reason": "mature", "description": "Image contains sensitive content"}}' \\
  "{ORIGIN}/v1/images/{identifier}/report/"
"""

image_oembed_curl = f"""
# Retrieve embedded content from an image's URL
curl \\
  {auth} \\
  "{ORIGIN}/v1/images/oembed/?url=https://wordpress.org/openverse/photos/{identifier}"
"""
