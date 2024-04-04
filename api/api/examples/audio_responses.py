from api.examples.environment import ORIGIN


identifier = "8624ba61-57f1-4f98-8a85-ece206c319cf"

base_audio = {
    "id": identifier,
    "title": "Wish You Were Here",
    "indexed_on": "2022-12-06T06:54:25Z",
    "foreign_landing_url": "https://www.jamendo.com/track/1214935",
    "url": "https://mp3d.jamendo.com/download/track/1214935/mp32",
    "creator": "The.madpix.project",
    "creator_url": "https://www.jamendo.com/artist/441585/the.madpix.project",
    "license": "by-nc-sa",
    "license_version": "3.0",
    "license_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
    "provider": "jamendo",
    "source": "jamendo",
    "category": "music",
    "genres": ["dance", "electronic", "house"],
    "filesize": 7139840,
    "filetype": "mp3",
    "tags": [
        {"accuracy": None, "name": "vocal"},
        {"accuracy": None, "name": "female"},
        {"accuracy": None, "name": "speed_medium"},
        {"accuracy": None, "name": "guitar"},
        {"accuracy": None, "name": "strings"},
        {"accuracy": None, "name": "energetic"},
        {"accuracy": None, "name": "acoustic"},
        {"accuracy": None, "name": "vocal"},
        {"accuracy": None, "name": "voice"},
        {"accuracy": None, "name": "funkyhouse"},
    ],
    "alt_files": None,
    "attribution": '"Wish You Were Here" by The.madpix.project is licensed under CC BY-NC-SA 3.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/3.0/.',  # noqa: E501,
    "fields_matched": [],
    "mature": False,
    "audio_set": {
        "title": "Wish You Were Here",
        "foreign_landing_url": "https://www.jamendo.com/album/145774/wish-you-were-here",  # noqa: E501
        "creator": "The.madpix.project",
        "creator_url": "https://www.jamendo.com/artist/441585/the.madpix.project",
        "url": "https://usercontent.jamendo.com?type=album&id=145774&width=200",
        "filesize": None,
        "filetype": None,
    },
    "duration": 270000,
    "bit_rate": 128000,
    "sample_rate": 44100,
    "thumbnail": f"{ORIGIN}/v1/audio/{identifier}/thumb/",
    "detail_url": f"{ORIGIN}/v1/audio/{identifier}/",
    "related_url": f"{ORIGIN}/v1/audio/{identifier}/related/",
    "waveform": f"{ORIGIN}/v1/audio/{identifier}/waveform/",
    "unstable__sensitivity": [],
}

audio_search_200_example = {
    "application/json": {
        "result_count": 1,
        "page_count": 1,
        "page_size": 20,
        "page": 1,
        "results": [
            base_audio | {"fields_matched": ["title"]},
        ],
        "warnings": [],
    },
}

audio_search_400_example = {
    "application/json": {
        "error": "InputError",
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",  # noqa: E501
        "fields": ["license"],
    }
}

audio_stats_200_example = {
    "application/json": [
        {
            "source_name": "freesound",
            "display_name": "Freesound",
            "source_url": "https://freesound.org/",
            "logo_url": None,
            "media_count": 827,
        },
        {
            "source_name": "jamendo",
            "display_name": "Jamendo",
            "source_url": "https://www.jamendo.com",
            "logo_url": None,
            "media_count": 180,
        },
        {
            "source_name": "wikimedia_audio",
            "display_name": "Wikimedia",
            "source_url": "https://commons.wikimedia.org",
            "logo_url": None,
            "media_count": 3992,
        },
        {
            "display_name": "CCMixter",
            "logo_url": None,
            "media_count": 1,
            "source_name": "ccmixter",
            "source_url": "https://ccmixter.org",
        },
    ]
}

audio_detail_200_example = {"application/json": base_audio}

audio_detail_404_example = {"application/json": {"detail": "Not found."}}

audio_related_200_example = {
    "application/json": {
        "result_count": 10000,
        "page_count": 1,
        "results": [
            {
                "title": "File:Mozart - Eine kleine Nachtmusik - 1. Allegro.ogg",
                "id": "36537842-b067-4ca0-ad67-e00ff2e06b2e",
                "creator": "Wolfgang Amadeus Mozart",
                "creator_url": "https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart",
                "url": "https://upload.wikimedia.org/wikipedia/commons/2/24/Mozart_-_Eine_kleine_Nachtmusik_-_1._Allegro.ogg",  # noqa: E501
                "provider": "wikimedia",
                "source": "wikimedia",
                "license": "by-sa",
                "license_version": "2.0",
                "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
                "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=3536953",  # noqa: E501
                "detail_url": f"{ORIGIN}/v1/audio/36537842-b067-4ca0-ad67-e00ff2e06b2e",  # noqa: E501
                "related_url": f"{ORIGIN}/v1/recommendations/audio/36537842-b067-4ca0-ad67-e00ff2e06b2e",  # noqa: E501
                "fields_matched": ["description", "title"],
                "tags": [{"name": "exam"}, {"name": "tactics"}],
            }
        ],
    }
}

audio_related_404_example = {
    "application/json": {"detail": "An internal server error occurred."}
}

audio_complain_201_example = {
    "application/json": {
        "identifier": identifier,
        "reason": "mature",
        "description": "This audio contains sensitive content",
    }
}

audio_waveform_200_example = {
    "application/json": {
        "len": 1083,
        "points": [
            0.61275,
            0.19593,
            0.74023,
            # 1077 more entries
            0.00089,
            0.00043,
            0.00049,
        ],
    }
}

audio_waveform_404_example = {
    "application/json": {"detail": "An internal server error occurred."}
}
