import os

token = os.getenv('AUDIO_REQ_TOKEN', 'DLBYIcfnKfolaXKcmMC8RIDCavc2hW')
origin = os.getenv('AUDIO_REQ_ORIGIN', 'https://api.openverse.engineering')

auth = f'-H "Authorization: Bearer {token}"' if token else ''
identifier = '440a0240-8b20-49e2-a4e6-6fee550fcc41'

syntax_examples = {
    "using single query parameter":
        'test',
    "using multiple query parameters":
        'test&license=pdm,by&categories=illustration&page_size=1&page=1',
    "that is an exact match of Giacomo Puccini":
        '"Giacomo Puccini"',
    "related to both dog and cat":
        'dog+cat',
    "related to dog or cat, but not necessarily both":
        'dog|cat',
    "related to dog but won't include results related to 'pug'":
        'dog -pug',
    "matching anything with the prefix 'net'":
        'net*',
    "matching dogs that are either corgis or labrador":
        'dogs + (corgis | labrador)',
    "matching strings close to the term theater "
    "with a difference of one character":
        'theatre~1',
}

audio_search_list_curl = '\n'.join(f"""
# Example {index}: Search for audio {purpose}
curl {auth} "{origin}/v1/audio/?q={syntax}"
""" for (index, (purpose, syntax)) in enumerate(syntax_examples.items()))

audio_search_curl = f"""
# Search for music titled "Friend" by Rob Costlow
curl {auth} "{origin}/v1/audio/?title=Friend&creator=Rob%20Costlow"
"""

audio_stats_curl = f"""
# Get the statistics for audio sources
curl {auth} "{origin}/v1/audio/stats/"
"""

audio_detail_curl = f"""
# Get the details of audio ID {identifier}
curl {auth} "{origin}/v1/audio/{identifier}/"
"""

audio_related_curl = f"""
# Get related audio files for audio ID {identifier}
curl {auth} "{origin}/v1/audio/{identifier}/related/"
"""

audio_complain_curl = f"""
# Report an issue about audio ID {identifier}
curl \\
  -X POST \\
  -H "Content-Type: application/json" \\
  {auth} \\
  -d '{{"reason": "mature", "description": "This audio contains sensitive content"}}' \\
  "{origin}/v1/audio/{identifier}/report/"
"""  # noqa
