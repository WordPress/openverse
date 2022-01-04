import os


origin = os.getenv("AUDIO_REQ_ORIGIN", "https://api.openverse.engineering")

identifier = "8624ba61-57f1-4f98-8a85-ece206c319cf"

base_audio = {
    "id": identifier,
    "title": "Wish You Were Here",
    "foreign_landing_url": "https://www.jamendo.com/track/1214935",
    "creator": "The.madpix.project",
    "creator_url": "https://www.jamendo.com/artist/441585/the.madpix.project",
    "url": "https://mp3d.jamendo.com/download/track/1214935/mp32",
    "license": "by-nc-sa",
    "license_version": "3.0",
    "license_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
    "provider": "jamendo",
    "source": "jamendo",
    "tags": [
        {"name": "vocal"},
        {"name": "female"},
        {"name": "speed_medium"},
        {"name": "guitar"},
        {"name": "strings"},
        {"name": "energetic"},
        {"name": "acoustic"},
        {"name": "vocal"},
        {"name": "voice"},
        {"name": "funkyhouse"},
    ],
    "genres": ["dance", "electronic", "house"],
    "thumbnail": f"{origin}/v1/audio/{identifier}/thumb/",
    "waveform": f"{origin}/v1/audio/{identifier}/waveform/",
    "detail_url": f"{origin}/v1/audio/{identifier}/",
    "related_url": f"{origin}/v1/audio/{identifier}/related/",
    "category": "music",
    "duration": 270000,
}

audio_search_200_example = {
    "application/json": {
        "result_count": 1,
        "page_count": 0,
        "page_size": 20,
        "page": 1,
        "results": [
            base_audio | {"fields_matched": ["title"]},
        ],
    },
}

audio_search_400_example = {
    "application/json": {
        "error": "InputError",
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",  # noqa
        "fields": ["license"],
    }
}

audio_stats_200_example = {
    "application/json": [
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
            "media_count": 4820,
        },
    ]
}

audio_detail_200_example = {
    "application/json": base_audio
    | {
        "attribution": '"Wish You Were Here" by The.madpix.project is licensed under CC-BY-NC-SA 3.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/3.0/.',  # noqa
        "audio_set": {
            "title": "Wish You Were Here",
            "foreign_landing_url": "https://www.jamendo.com/album/145774/wish-you-were-here",  # noqa
            "creator": "The.madpix.project",
            "creator_url": "https://www.jamendo.com/artist/441585/the.madpix.project",
            "url": "https://usercontent.jamendo.com?type=album&id=145774&width=200",
            "filesize": None,
            "filetype": None,
        },
        "duration": 270000,
        "bit_rate": None,
        "sample_rate": None,
        "alt_files": None,
        "filesize": None,
        "filetype": "mp3",
    },
}

audio_detail_404_example = {"application/json": {"detail": "Not found."}}

audio_related_200_example = {
    "application/json": {
        "result_count": 10000,
        "page_count": 0,
        "results": [
            {
                "title": "File:Mozart - Eine kleine Nachtmusik - 1. Allegro.ogg",  # noqa
                "id": "36537842-b067-4ca0-ad67-e00ff2e06b2e",
                "creator": "Wolfgang Amadeus Mozart",
                "creator_url": "https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart",  # noqa
                "url": "https://upload.wikimedia.org/wikipedia/commons/2/24/Mozart_-_Eine_kleine_Nachtmusik_-_1._Allegro.ogg",  # noqa
                "provider": "wikimedia",
                "source": "wikimedia",
                "license": "by-sa",
                "license_version": "2.0",
                "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",  # noqa
                "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=3536953",  # noqa
                "detail_url": "http://api.openverse.engineering/v1/audio/36537842-b067-4ca0-ad67-e00ff2e06b2e",  # noqa
                "related_url": "http://api.openverse.engineering/v1/recommendations/audio/36537842-b067-4ca0-ad67-e00ff2e06b2e",  # noqa
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
