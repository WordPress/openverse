"""
This file holds the default provider names for each provider API and a
dictionary of related sub providers. The key of the dictionary reflects
the sub provider name and the corresponding item is a value (or set of values)
from the API response which helps to identify the sub provider.

Apart from that, this file stores other provider related information which
might be useful for retrieving sub-providers at the database level and the
API level.
"""

# Flickr parameters
FLICKR_DEFAULT_PROVIDER = 'flickr'

FLICKR_SUB_PROVIDERS = {
    'nasa': {
        '24662369@N07',  # NASA Goddard Photo and Video
        '35067687@N04',  # NASA HQ PHOTO
        '29988733@N04',  # NASA Johnson
        '28634332@N05',  # NASA's Marshall Space Flight Center
        '108488366@N07',  # NASAKennedy
        '136485307@N06'  # Apollo Image Gallery
    },
    'bio_diversity': {
        '61021753@N02'  # BioDivLibrary
    },
    'spacex': {
        '130608600@N05'  # Official SpaceX Photos
    }
}

FLICKR_PHOTO_URL_BASE = 'https://www.flickr.com/photos/'

# Europeana parameters
EUROPEANA_DEFAULT_PROVIDER = 'europeana'

EUROPEANA_SUB_PROVIDERS = {
    'wellcome_collection': "Wellcome Collection"
}
