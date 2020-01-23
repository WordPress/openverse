from enum import Enum, auto

"""
https://github.com/creativecommons/cccatalog-api/issues/340

Attempt to figure out the image type (illustration, vector, photograph, or
digitized artwork) based on its source and file extension.
"""


class Category(Enum):
    PHOTOGRAPH = auto()
    DIGITIZED_ARTWORK = auto()
    ILLUSTRATION = auto()


# Map each provider to a set of categories..
provider_category = {
    '__default': [],
    'thorvaldsenmuseum': [Category.DIGITIZED_ARTWORK],
    'svgsilh': [Category.ILLUSTRATION],
    'phylopic': [Category.ILLUSTRATION],
    'floraon': [Category.PHOTOGRAPH],
    'animaldiversity': [Category.PHOTOGRAPH],
    'WoRMS': [Category.PHOTOGRAPH],
    'clevelandmuseum': [Category.DIGITIZED_ARTWORK],
    'CAPL': [Category.PHOTOGRAPH],
    'sciencemuseum': [Category.PHOTOGRAPH],
    'rijksmuseum': [Category.DIGITIZED_ARTWORK],
    'museumsvictoria': [Category.DIGITIZED_ARTWORK],
    'met': [Category.DIGITIZED_ARTWORK],
    'mccordmuseum': [Category.DIGITIZED_ARTWORK],
    'digitaltmuseum': [Category.DIGITIZED_ARTWORK],
    'deviantart': [Category.DIGITIZED_ARTWORK],
    'brooklynmuseum': [Category.DIGITIZED_ARTWORK]
}


def get_categories(extension, provider):
    if extension and extension.lower() == 'svg':
        categories = [Category.ILLUSTRATION]
    elif provider in provider_category:
        categories = provider_category[provider]
    else:
        categories = provider_category['__default']
    return [x.name for x in categories]
