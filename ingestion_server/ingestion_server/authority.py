"""
Authority is a ranking indicating the pedigree of an image.

It ranges from 0 (least authoritative) to 100 (most authoritative). Some examples of
things that could impact authority are:
- The reputation of the website that posted an image
- The popularity of the uploader on a social media site in terms of number of
followers
- Whether the uploader has uploaded images that have previously been flagged for
copyright infringement.
- etc

The authority can be set from the catalog layer through the meta_data field
or through the ingestion layer. As of now, we are only factoring in the
reputation of the website as a static hand-picked list based on experience
and search result quality, with the intention to add more sophisticated and
tailored measures of authority later on.

Also note that this is just one factor in rankings, and the magnitude of the
boost can be adjusted at search-time.
"""

from enum import Enum, auto


class AuthorityTypes(Enum):
    CURATED = auto()
    CULTURAL_INSTITUTION = auto()
    SOCIAL_MEDIA = auto()
    DEFAULT = auto()


# We want to boost curated collections where each image has been vetted for
# cultural significance.
boost = {
    AuthorityTypes.CURATED: 85,
    AuthorityTypes.CULTURAL_INSTITUTION: 90,
    AuthorityTypes.SOCIAL_MEDIA: 75,
    AuthorityTypes.DEFAULT: 80,
}

authority_types = {
    "flickr": AuthorityTypes.SOCIAL_MEDIA,
    "behance": AuthorityTypes.SOCIAL_MEDIA,
    "thingiverse": AuthorityTypes.SOCIAL_MEDIA,
    "sketchfab": AuthorityTypes.SOCIAL_MEDIA,
    "deviantart": AuthorityTypes.SOCIAL_MEDIA,
    "thorvaldsensmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "svgsilh": AuthorityTypes.CULTURAL_INSTITUTION,
    "smithsonian": AuthorityTypes.CULTURAL_INSTITUTION,
    "rijksmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "museumsvictoria": AuthorityTypes.CULTURAL_INSTITUTION,
    "met": AuthorityTypes.CULTURAL_INSTITUTION,
    "mccordsmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "digitaltmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "clevelandmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "brooklynmuseum": AuthorityTypes.CULTURAL_INSTITUTION,
    "stocksnap": AuthorityTypes.CURATED,
    "rawpixel": AuthorityTypes.CURATED,
}


def get_authority_boost(source):
    authority_boost = None
    if source in authority_types:
        authority_type = authority_types[source]
        if authority_type in boost:
            authority_boost = boost[authority_type]
        else:
            authority_boost = boost[AuthorityTypes.DEFAULT]
    return authority_boost
