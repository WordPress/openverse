import os


origin = os.getenv("AUDIO_REQ_ORIGIN", "https://api.openverse.engineering")

identifier = "29cb352c-60c1-41d8-bfa1-7d6f7d955f63"

base_image = {
    "id": identifier,
    "title": "Bust of Patroclus (photograph; calotype; salt print)",
    "foreign_landing_url": "https://collection.sciencemuseumgroup.org.uk/objects/co8554747/bust-of-patroclus-photograph-calotype-salt-print",  # noqa
    "creator": "William Henry Fox Talbot",
    "url": "https://coimages.sciencemuseumgroup.org.uk/images/439/67/large_1937_1281_0001__0001_.jpg",  # noqa
    "license": "by-nc-nd",
    "license_version": "4.0",
    "license_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "provider": "sciencemuseum",
    "source": "sciencemuseum",
    "thumbnail": f"{origin}/v1/images/{identifier}/thumb/",
    "detail_url": f"{origin}/v1/images/{identifier}/",
    "related_url": f"{origin}/v1/images/{identifier}/related/",
}

image_search_200_example = {
    "application/json": {
        "result_count": 1,
        "page_count": 0,
        "page_size": 20,
        "page": 1,
        "results": [
            base_image
            | {
                "fields_matched": ["title"],
            }
        ],
    },
}

image_search_400_example = {
    "application/json": {
        "error": "InputError",
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",  # noqa
        "fields": ["license"],
    }
}

image_stats_200_example = {
    "application/json": [
        {
            "source_name": "flickr",
            "display_name": "Flickr",
            "source_url": "https://www.flickr.com",
            "logo_url": None,
            "media_count": 1000,
        },
        {
            "source_name": "rawpixel",
            "display_name": "rawpixel",
            "source_url": "https://www.rawpixel.com",
            "logo_url": None,
            "media_count": 1000,
        },
        {
            "source_name": "sciencemuseum",
            "display_name": "Science Museum",
            "source_url": "https://www.sciencemuseum.org.uk",
            "logo_url": None,
            "media_count": 1000,
        },
        {
            "source_name": "stocksnap",
            "display_name": "StockSnap",
            "source_url": "https://stocksnap.io",
            "logo_url": None,
            "media_count": 1000,
        },
        {
            "source_name": "wikimedia",
            "display_name": "Wikimedia",
            "source_url": "https://commons.wikimedia.org",
            "logo_url": None,
            "media_count": 1000,
        },
    ]
}

image_detail_200_example = {
    "application/json": base_image
    | {
        "attribution": '"Bust of Patroclus (photograph; calotype; salt print)" by William Henry Fox Talbot is licensed under CC-BY-NC-ND 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-nd/4.0/.',  # noqa
        "height": 1536,
        "width": 1276,
        "tags": None,
        "creator_url": None,
    }
}

image_detail_404_example = {"application/json": {"detail": "Not found."}}

image_related_200_example = {
    "application/json": {
        "result_count": 10000,
        "page_count": 0,
        "results": [
            {
                "title": "exam tactics",
                "id": "610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                "creator": "Sean MacEntee",
                "creator_url": "https://www.flickr.com/photos/18090920@N07",
                "tags": [{"name": "exam"}, {"name": "tactics"}],
                "url": "https://live.staticflickr.com/4065/4459771899_07595dc42e.jpg",  # noqa
                "thumbnail": "https://api.openverse.engineering/v1/thumbs/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa
                "provider": "flickr",
                "source": "flickr",
                "license": "by",
                "license_version": "2.0",
                "license_url": "https://creativecommons.org/licenses/by/2.0/",
                "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/4459771899",  # noqa
                "detail_url": "http://api.openverse.engineering/v1/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa
                "related_url": "http://api.openverse.engineering/v1/recommendations/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa
            }
        ],
    }
}

image_related_404_example = {
    "application/json": {"detail": "An internal server error occurred."}
}

image_oembed_200_example = {
    "application/json": {
        "version": "1.0",
        "type": "photo",
        "width": 1276,
        "height": 1536,
        "title": "Bust of Patroclus (photograph; calotype; salt print)",
        "author_name": "William Henry Fox Talbot",
        "author_url": None,
        "license_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    }
}

image_oembed_404_example = {
    "application/json": {"detail": "An internal server error occurred."}
}

image_complain_201_example = {
    "application/json": {
        "identifier": identifier,
        "reason": "mature",
        "description": "This image contains sensitive content",
    }
}
