from api.examples.environment import ORIGIN, TOKEN


auth = f'-H "Authorization: Bearer {TOKEN}"' if TOKEN else ""
identifier = "8624ba61-57f1-4f98-8a85-ece206c319cf"

syntax_examples = {
    "using single query parameter": "test",
    "using multiple query parameters": "test&license=pdm,by&categories=illustration&page_size=1&page=1",  # noqa: E501
    "that is an exact match of Giacomo Puccini": r"%22Giacomo%20Puccini%22",
    "related to both dog and cat": "dog+cat",
    "related to dog or cat, but not necessarily both": "dog|cat",
    "related to dog but won't include results related to 'pug'": "dog -pug",
    "matching anything with the prefix 'net'": "net*",
    "matching dogs that are either corgis or labrador": "dogs + (corgis | labrador)",
    "matching strings close to the term theater "
    "with a difference of one character": "theatre~1",
}

audio_search_list_curl = "\n".join(
    f"""
# Example {index}: Search for audio {purpose}
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/?q={syntax}"
"""
    for (index, (purpose, syntax)) in enumerate(syntax_examples.items())
)

audio_search_curl = f"""
# Search for music titled "Wish You Were Here" by The.madpix.project
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/?title=Wish%20You%20Were%20Here&creator=The.madpix.project"
"""

audio_stats_curl = f"""
# Get the statistics for audio sources
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/stats/"
"""

audio_detail_curl = f"""
# Get the details of audio ID {identifier}
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/{identifier}/"
"""

audio_related_curl = f"""
# Get related audio files for audio ID {identifier}
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/{identifier}/related/"
"""

audio_complain_curl = f"""
# Report an issue about audio ID {identifier}
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  {auth} \\
  -d '{{"reason": "mature", "description": "This audio contains sensitive content"}}' \\
  "{ORIGIN}/v1/audio/{identifier}/report/"
"""

audio_waveform_curl = f"""
# Get the waveform of audio ID {identifier}
curl \\
  {auth} \\
  "{ORIGIN}/v1/audio/{identifier}/waveform/"
"""
