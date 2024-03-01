"""
This file holds the default provider names for each provider API and a
dictionary of related sub providers. The key of the dictionary reflects
the sub provider name and the corresponding item is a value (or set of values)
from the API response which helps to identify the sub provider.

Apart from that, this file stores other provider related information which
might be useful for retrieving sub-providers at the database level and the
API level.
"""

import os


# Default provider names
AUCKLAND_MUSEUM_IMAGE_PROVIDER = "aucklandmuseum_tamakipaengahira"
BROOKLYN_DEFAULT_PROVIDER = "brooklynmuseum"
CLEVELAND_DEFAULT_PROVIDER = "clevelandmuseum"
EUROPEANA_DEFAULT_PROVIDER = "europeana"
FINNISH_DEFAULT_PROVIDER = "finnishmuseums"
FLICKR_DEFAULT_PROVIDER = "flickr"
FREESOUND_DEFAULT_PROVIDER = "freesound"
INATURALIST_DEFAULT_PROVIDER = "inaturalist"
JAMENDO_DEFAULT_PROVIDER = "jamendo"
JUSTTAKEITFREE_IMAGE_PROVIDER = "justtakeitfree"
METROPOLITAN_MUSEUM_DEFAULT_PROVIDER = "met"
NAPPY_DEFAULT_PROVIDER = "nappy"
NYPL_DEFAULT_PROVIDER = "nypl"
RAWPIXEL_DEFAULT_PROVIDER = "rawpixel"
SCIENCE_DEFAULT_PROVIDER = "sciencemuseum"
SMITHSONIAN_DEFAULT_PROVIDER = "smithsonian"
SMK_DEFAULT_PROVIDER = "smk"
STOCKSNAP_DEFAULT_PROVIDER = "stocksnap"
VICTORIA_DEFAULT_PROVIDER = "museumsvictoria"
WALTERS_DEFAULT_PROVIDER = "waltersartmuseum"
WIKIMEDIA_AUDIO_PROVIDER = "wikimedia_audio"
WIKIMEDIA_DEFAULT_PROVIDER = "wikimedia"
WORDPRESS_DEFAULT_PROVIDER = "wordpress"
PHYLOPIC_DEFAULT_PROVIDER = "phylopic"
CC_MIXTER_DEFAULT_PROVIDER = "ccmixter"

# Finnish parameters
FINNISH_SUB_PROVIDERS = {
    "national_museum_of_finland": "0/Suomen kansallismuseo/",
    "finnish_heritage_agency": "0/Museovirasto/",
    "finnish_satakunnan_museum": "0/SATMUSEO/",
    "finnish_military_museum": "0/SA-kuva/",
}

# Flickr parameters
FLICKR_SUB_PROVIDERS = {
    "nasa": {
        "24662369@N07",  # NASA Goddard Photo and Video
        "35067687@N04",  # NASA HQ PHOTO
        "29988733@N04",  # NASA Johnson
        "28634332@N05",  # NASA's Marshall Space Flight Center
        "108488366@N07",  # NASAKennedy
        "136485307@N06",  # Apollo Image Gallery
    },
    "bio_diversity": {"61021753@N02"},  # BioDivLibrary
    "spacex": {"130608600@N05"},  # Official SpaceX Photos
    "woc_tech": {"136629440@N06"},  # WOCinTech Chat
    "valence_romans": {"150408343@N02"},  # Valence Romans Agglomeration Media Library
    "east_riding": {"138361426@N08"},  # East Riding Archives
    "archief_alkmaar": {"98304311@N03"},  # Regionaal Archief Alkmaar Commons
    "bib_gulbenkian": {"26577438@N06"},  # Gulbenkian Art Library
}

FLICKR_PHOTO_URL_BASE = "https://www.flickr.com/photos/"

# Europeana parameters
EUROPEANA_SUB_PROVIDERS = {"wellcome_collection": "Wellcome Collection"}

# Smithsonian parameters
SMITHSONIAN_SUB_PROVIDERS = {
    "smithsonian_national_museum_of_natural_history": {
        "NMNHANTHRO",  # NMNH - Anthropology Dept.
        "NMNHBIRDS",  # NMNH - Vertebrate Zoology - Birds Division
        "NMNHBOTANY",  # NMNH - Botany Dept.
        "NMNHEDUCATION",  # NMNH - Education & Outreach
        "NMNHENTO",  # NMNH - Entomology Dept.
        "NMNHFISHES",  # NMNH - Vertebrate Zoology - Fishes Division
        "NMNHHERPS",  # NMNH - Vertebrate Zoology - Herpetology Division
        "NMNHINV",  # NMNH - Invertebrate Zoology Dept.
        "NMNHMAMMALS",  # NMNH - Vertebrate Zoology - Mammals Division
        "NMNHMINSCI",  # NMNH - Mineral Sciences Dept.
        "NMNHPALEO",  # NMNH - Paleobiology Dept.
    },
    "smithsonian_anacostia_museum": {"ACM"},  # Anacostia Community Museum
    "smithsonian_cooper_hewitt_museum": {
        "CHNDM"  # Cooper Hewitt, Smithsonian Design Museum
    },
    "smithsonian_field_book_project": {"FBR"},  # Smithsonian Field Book Project
    "smithsonian_freer_gallery_of_art": {
        "FSG"  # Freer Gallery of Art and Arthur M. Sackler Gallery
    },
    "smithsonian_gardens": {
        "HAC",  # Smithsonian Gardens
        "OFEO-SG",  # Office of Facilities Engineering and Operations
    },
    "smithsonian_hirshhorn_museum": {"HMSG"},  # Hirshhorn Museum and Sculpture Garden
    "smithsonian_air_and_space_museum": {"NASM"},  # National Air and Space Museum
    "smithsonian_african_american_history_museum": {
        "NMAAHC"  # National Museum of African American History and Culture
    },
    "smithsonian_american_history_museum": {
        "NMAH"  # National Museum of American History
    },
    "smithsonian_american_indian_museum": {
        "NMAI"  # National Museum of the American Indian
    },
    "smithsonian_african_art_museum": {"NMAfA"},  # National Museum of African Art
    "smithsonian_portrait_gallery": {"NPG"},  # National Portrait Gallery
    "smithsonian_postal_museum": {"NPM"},  # National Postal Museum
    "smithsonian_zoo_and_conservation": {
        "NZP"  # Smithsonian's National Zoo & Conservation Biology Institute
    },
    "smithsonian_american_art_museum": {"SAAM"},  # Smithsonian American Art Museum
    "smithsonian_institution_archives": {"SIA"},  # Smithsonian Institution Archives
    "smithsonian_libraries": {"SIL"},  # Smithsonian Libraries
    "smithsonian_ralph_rinzler_archive": {
        "CFCHFOLKLIFE"  # Ralph Rinzler Folklife Archives and Collections
    },
}

# User-Agent header for APIs that require it
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")

CANONICAL_DOMAIN: str = os.getenv("CANONICAL_DOMAIN", "openverse.org")

_proto = "http" if "localhost" in CANONICAL_DOMAIN else "https"
CANONICAL_ORIGIN: str = f"{_proto}://{CANONICAL_DOMAIN}"

UA_STRING = f"Openverse/0.1 ({CANONICAL_ORIGIN}; {CONTACT_EMAIL})"


# Available Image Categories for API
class ImageCategory:
    PHOTOGRAPH = "photograph"
    DIGITIZED_ARTWORK = "digitized_artwork"
    ILLUSTRATION = "illustration"


# Available Audio Categories for API
class AudioCategory:
    AUDIOBOOK = "audiobook"
    MUSIC = "music"
    NEWS = "news"
    PODCAST = "podcast"
    PRONUNCIATION = "pronunciation"
    SOUND_EFFECT = "sound_effect"


# Default image category by source
DEFAULT_IMAGE_CATEGORY = {
    "stocksnap": ImageCategory.PHOTOGRAPH,
    # Remains to be assigned
    "animaldiversity": ImageCategory.PHOTOGRAPH,
    "brooklynmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "capl": ImageCategory.PHOTOGRAPH,
    "clevelandmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "deviantart": ImageCategory.DIGITIZED_ARTWORK,
    "digitaltmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "floraon": ImageCategory.PHOTOGRAPH,
    "inaturalist": ImageCategory.PHOTOGRAPH,
    "mccordmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "met": ImageCategory.DIGITIZED_ARTWORK,
    "museumsvictoria": ImageCategory.DIGITIZED_ARTWORK,
    "nappy": ImageCategory.PHOTOGRAPH,
    "phylopic": ImageCategory.ILLUSTRATION,
    "rijksmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "sciencemuseum": ImageCategory.PHOTOGRAPH,
    "svgsilh": ImageCategory.ILLUSTRATION,
    "thorvaldsenmuseum": ImageCategory.DIGITIZED_ARTWORK,
    "worms": ImageCategory.PHOTOGRAPH,
}
