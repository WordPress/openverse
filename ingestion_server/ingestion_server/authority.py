from enum import Enum, auto
"""
Authority is a ranking from 0 to 100 (with 0 being least authoritative)
indicating the pedigree of an image. Some examples of things that could impact
authority:
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


class AuthorityTypes(Enum):
    CURATED = auto()
    SOCIAL_MEDIA = auto()


# We want to boost curated collections where each image has been vetted for
# cultural significance.
boost = {
    AuthorityTypes.CURATED: 100
}
# Social media sites receive a (light) penalty because the quality
# of the images is highly variable. High quality results from social media
# should still float to the top based on popularity metrics.
penalize = {
    AuthorityTypes.SOCIAL_MEDIA: 10
}

authority_types = {
    'flickr': AuthorityTypes.SOCIAL_MEDIA,
    'behance': AuthorityTypes.SOCIAL_MEDIA,
    'thingiverse': AuthorityTypes.SOCIAL_MEDIA,
    'sketchfab': AuthorityTypes.SOCIAL_MEDIA,
    'deviantart': AuthorityTypes.SOCIAL_MEDIA,
    'thorvaldsensmuseum': AuthorityTypes.CURATED,
    'svgsilh': AuthorityTypes.CURATED,
    'smithsonian': AuthorityTypes.CURATED,
    'rijksmuseum': AuthorityTypes.CURATED,
    'museumsvictoria': AuthorityTypes.CURATED,
    'met': AuthorityTypes.CURATED,
    'mccordsmuseum': AuthorityTypes.CURATED,
    'digitaltmuseum': AuthorityTypes.CURATED
}


def get_authority_boost(provider):
    authority_boost = None
    if provider in authority_types:
        authority_type = authority_types[provider]
        if authority_type in boost:
            authority_boost = boost[authority_type]
    return authority_boost


def get_authority_penalty(provider):
    authority_penalty = None
    if provider in authority_types:
        authority_type = authority_types[provider]
        if authority_type in penalize:
            authority_penalty = penalize[authority_type]
    return authority_penalty
