audio_search_200_example = {
    "application/json": {
        "result_count": 77,
        "page_count": 77,
        "page_size": 1,
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
                "fields_matched": [
                    "description",
                    "title"
                ]
            }
        ]
    },
}

audio_search_400_example = {
    "application/json": {
        "error": "InputError",
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",  # noqa
        "fields": [
            "license"
        ]
    }
}

recommendations_audio_read_200_example = {
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
                "fields_matched": [
                    "description",
                    "title"
                ],
                "tags": [
                    {
                        "name": "exam"
                    },
                    {
                        "name": "tactics"
                    }
                ],
            }
        ]
    }
}

recommendations_audio_read_404_example = {
    "application/json": {
        "detail": "An internal server error occurred."
    }
}

audio_detail_200_example = {
    "application/json": {
        # TODO
    }
}

audio_detail_404_example = {
    "application/json": {
        "detail": "Not found."
    }
}

audio_report_create_201_example = {
    "application/json": {
        "id": 10,
        "identifier": "7c829a03-fb24-4b57-9b03-65f43ed19395",
        "reason": "mature",
        "description": "This audio contains sensitive content"
    }
}

audio_stats_200_example = {
    "application/json": [
        {
            "source_name": "jamendo",
            "audio_count": 123456789,
            "display_name": "Jamendo",
            "source_url": "https://www.jamendo.com"
        }
    ]
}
