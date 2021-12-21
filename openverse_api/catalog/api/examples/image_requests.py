import os


token = os.getenv("AUDIO_REQ_TOKEN", "DLBYIcfnKfolaXKcmMC8RIDCavc2hW")
origin = os.getenv("AUDIO_REQ_ORIGIN", "https://api.openverse.engineering")

auth = f'-H "Authorization: Bearer {token}"' if token else ""
identifier = "cdbd3bf6-1745-45bb-b399-61ee149cd58a"

syntax_examples = {
    "using single query parameter": "test",
    "using multiple query parameters": "test&license=pdm,by&categories=illustration&page_size=1&page=1",  # noqa: E501
    "that are an exact match of Claude Monet": '"Claude Monet"',
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
curl {auth} "{origin}/v1/images/?q={syntax}"
"""
    for (index, (purpose, syntax)) in enumerate(syntax_examples.items())
)

image_search_curl = f"""
# Search for images titled "Bust" by Talbot
curl {auth} "{origin}/v1/images/?title=Train&creator=Trolle"
"""

image_stats_curl = f"""
# Get the statistics for image sources
curl {auth} "{origin}/v1/images/stats/"
"""

image_detail_curl = f"""
# Get the details of image ID {identifier}
curl {auth} "{origin}/v1/images/{identifier}/"
"""

image_related_curl = f"""
# Get related images for image ID {identifier}
curl {auth} "{origin}/v1/images/{identifier}/related/"
"""

image_complain_curl = f"""
# Report an issue about image ID {identifier}
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  {auth} \\
  -d '{{"reason": "mature", "description": "This image contains sensitive content"}}' \\
  "{origin}/v1/images/{identifier}/report/"
"""  # noqa

image_oembed_curl = f"""
# Retrieve embedded content from image URL (https://wordpress.org/openverse/photos/{identifier})
curl {auth} "{origin}/v1/images/oembed/?url=https://wordpress.org/openverse/photos/{identifier}"
"""  # noqa
