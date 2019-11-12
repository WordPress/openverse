import enum

"""
https://github.com/creativecommons/cccatalog-api/issues/340

Attempt to figure out the image type (illustration, vector, photograph, or
digitized artwork) based on its source and file extension.
"""


class Category(enum.Enum):
    VECTOR = 0
    PHOTOGRAPH = 1
    DIGITIZED_ARTWORK = 2
    ILLUSTRATION = 3


# Map each provider to a set of categories..
provider_category = {
    '__default': [Category.ILLUSTRATION],
    'thorvaldsenmuseum': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'svgsilh': [Category.VECTOR, Category.ILLUSTRATION],
    'thingiverse': [Category.ILLUSTRATION],
    'sciencemuseum': [Category.PHOTOGRAPH, Category.PHOTOGRAPH],
    'rijksmuseum': [
        Category.ILLUSTRATION, Category.PHOTOGRAPH, Category.DIGITIZED_ARTWORK
    ],
    'rawpixel': [
        Category.PHOTOGRAPH, Category.DIGITIZED_ARTWORK, Category.VECTOR
    ],
    'phylopic': [Category.VECTOR, Category.ILLUSTRATION],
    'museumsvictoria': [
        Category.PHOTOGRAPH, Category.DIGITIZED_ARTWORK, Category.ILLUSTRATION
    ],
    'met': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'mccordmuseum': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'geographorguk': [Category.PHOTOGRAPH],
    'flickr': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'floraon': [Category.PHOTOGRAPH],
    'digitaltmuseum': [
        Category.PHOTOGRAPH, Category.DIGITIZED_ARTWORK, Category.ILLUSTRATION
    ],
    'deviantart': [
        Category.PHOTOGRAPH, Category.DIGITIZED_ARTWORK, Category.ILLUSTRATION,
        Category.VECTOR
    ],
    'clevelandmuseum': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'brooklynmuseum': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'behance': [
        Category.PHOTOGRAPH, Category.ILLUSTRATION, Category.DIGITIZED_ARTWORK
    ],
    'animaldiversity': [Category.PHOTOGRAPH],
    'WoRMS': [Category.PHOTOGRAPH],
    'CAPL': [Category.PHOTOGRAPH]
}


def _serialize(categories):
    """
    Convert enum to an appropriate representation for storage in Elasticsearch.
    """
    return [x.name for x in categories]


def get_categories(extension, provider):
    if extension.lower() == 'svg':
        categories = [Category.VECTOR, Category.ILLUSTRATION]
    elif provider in provider_category:
        categories = provider_category[provider]
    else:
        categories = provider_category['__default']
    return _serialize(categories)

