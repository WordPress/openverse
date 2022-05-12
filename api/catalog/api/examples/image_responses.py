import os


origin = os.getenv("AUDIO_REQ_ORIGIN", "https://api.openverse.engineering")

identifier = "cdbd3bf6-1745-45bb-b399-61ee149cd58a"

base_image = {
    "id": identifier,
    "title": "Train area in Copenhagen South / Tog område i Syd København",
    "foreign_landing_url": "https://www.flickr.com/photos/126744325@N07/51745389858",
    "creator": "Kristoffer Trolle",
    "creator_url": "https://www.flickr.com/photos/126744325@N07",
    "url": "https://live.staticflickr.com/65535/51745389858_c10358e1a3_b.jpg",
    "license": "by",
    "license_version": "2.0",
    "license_url": "https://creativecommons.org/licenses/by/2.0/",
    "provider": "flickr",
    "source": "flickr",
    "category": "photograph",
    "tags": [
        {"name": "copenhagen"},
        {"name": "danmark"},
        {"name": "denmark"},
        {"name": "dsb"},
        {"name": "fujifilmxf35mmf2rwr"},
        {"name": "fujifilmxh1"},
        {"name": "københavn"},
        {"name": "område"},
        {"name": "south"},
        {"name": "syd"},
        {"name": "tiffenblackpromist14filter"},
        {"name": "tog"},
        {"name": "train"},
    ],
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
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",  # noqa: E501
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
            "media_count": 2500,
        },
        {
            "source_name": "stocksnap",
            "display_name": "StockSnap",
            "source_url": "https://stocksnap.io",
            "logo_url": None,
            "media_count": 2500,
        },
    ]
}

image_detail_200_example = {
    "application/json": base_image
    | {
        "attribution": '"Train area in Copenhagen South / Tog område i Syd København" by Kristoffer Trolle is licensed under CC BY 2.0. To view a copy of this license, visit https://creativecommons.org/licenses/by/2.0/.',  # noqa: E501
        "height": 683,
        "width": 1024,
        "filesize": "157497",
        "filetype": "jpg",
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
                "url": "https://live.staticflickr.com/4065/4459771899_07595dc42e.jpg",  # noqa: E501
                "thumbnail": "https://api.openverse.engineering/v1/thumbs/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa: E501
                "provider": "flickr",
                "source": "flickr",
                "license": "by",
                "license_version": "2.0",
                "license_url": "https://creativecommons.org/licenses/by/2.0/",
                "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/4459771899",  # noqa: E501
                "detail_url": "http://api.openverse.engineering/v1/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa: E501
                "related_url": "http://api.openverse.engineering/v1/recommendations/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",  # noqa: E501
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
        "width": 1024,
        "height": 683,
        "title": "Train area in Copenhagen South / Tog område i Syd København",
        "author_name": "Kristoffer Trolle",
        "author_url": "https://www.flickr.com/photos/126744325@N07",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
    }
}

image_oembed_404_example = {
    "application/json": {"detail": "An internal server error occurred."}
}

image_complain_201_example = {
    "application/json": {
        "identifier": identifier,
        "reason": "mature",
        "description": "Image contains sensitive content",
    }
}
