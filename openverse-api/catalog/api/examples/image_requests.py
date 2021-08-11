syntax_examples = {
    "using single query parameter":
        'test',
    "using multiple query parameters":
        'test&license=pdm,by&categories=illustration&page_size=1&page=1',
    "that are an exact match of Claude Monet":
        '"Claude Monet"',
    "related to both dog and cat":
        'dog+cat',
    "related to dog or cat, but not necessarily both":
        'dog|cat',
    "related to dog but won't include results related to 'pug'":
        'dog -pug',
    "matching anything with the prefix ‘net’":
        'net*',
    "matching dogs that are either corgis or labrador":
        'dogs + (corgis | labrador)',
    "matching strings close to the term theater"
    "with a difference of one character":
        'theatre~1',
}

image_search_curl = '\n\n'.join([
    (f'# Example {index}: Search for images {purpose}\n'
     'curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" '
     f'https://api.openverse.engineering/v1/images?q={syntax}')
    for (index, (purpose, syntax)) in enumerate(syntax_examples.items())
])

recommendations_images_read_curl = """
# Get related images for image ID 7c829a03-fb24-4b57-9b03-65f43ed19395
curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.openverse.engineering/v1/recommendations/images/7c829a03-fb24-4b57-9b03-65f43ed19395
"""  # noqa

image_detail_curl = """
# Get the details of image ID 7c829a03-fb24-4b57-9b03-65f43ed19395
curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.openverse.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395
"""  # noqa

image_stats_curl = """
# Get the statistics for image sources
curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.openverse.engineering/v1/images/stats
"""  # noqa
