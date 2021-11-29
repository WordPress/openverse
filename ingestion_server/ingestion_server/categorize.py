"""
https://github.com/creativecommons/cccatalog-api/issues/340

Attempt to figure out the image type (illustration, vector, photograph, or
digitized artwork) based on its source and file extension.
"""

from enum import Enum, auto


class Category(Enum):
    PHOTOGRAPH = auto()
    DIGITIZED_ARTWORK = auto()
    ILLUSTRATION = auto()


# One-to-one mapping of providers to categories
source_category = {
    "__default": None,
    "thorvaldsenmuseum": Category.DIGITIZED_ARTWORK,
    "svgsilh": Category.ILLUSTRATION,
    "phylopic": Category.ILLUSTRATION,
    "floraon": Category.PHOTOGRAPH,
    "animaldiversity": Category.PHOTOGRAPH,
    "WoRMS": Category.PHOTOGRAPH,
    "clevelandmuseum": Category.DIGITIZED_ARTWORK,
    "CAPL": Category.PHOTOGRAPH,
    "sciencemuseum": Category.PHOTOGRAPH,
    "rijksmuseum": Category.DIGITIZED_ARTWORK,
    "museumsvictoria": Category.DIGITIZED_ARTWORK,
    "met": Category.DIGITIZED_ARTWORK,
    "mccordmuseum": Category.DIGITIZED_ARTWORK,
    "digitaltmuseum": Category.DIGITIZED_ARTWORK,
    "deviantart": Category.DIGITIZED_ARTWORK,
    "brooklynmuseum": Category.DIGITIZED_ARTWORK,
}


def get_category(extension, source):
    """
    Return the category of an image based on its extension and source.
    :param extension: the file extension of the image
    :param source: the source providing this image
    :return: the category of this image
    """

    if extension and extension.lower() == "svg":
        category = Category.ILLUSTRATION
    elif source in source_category:
        category = source_category[source]
    else:
        category = None
    return category.name.lower() if category is not None else None
