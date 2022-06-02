import os


origin = os.getenv("AUDIO_REQ_ORIGIN", "https://api.openverse.engineering")

identifier = "4bc43a04-ef46-4544-a0c1-63c63f56e276"

base_image = {
    "id": identifier,
    "title": "Tree Bark Photo",
    "foreign_landing_url": "https://stocksnap.io/photo/XNVBVXO3B7",
    "url": "https://cdn.stocksnap.io/img-thumbs/960w/XNVBVXO3B7.jpg",
    "creator": "Tim Sullivan",
    "creator_url": "https://www.secretagencygroup.com",
    "license": "cc0",
    "license_version": "1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "provider": "stocksnap",
    "source": "stocksnap",
    "category": "photograph",
    "filesize": None,
    "filetype": None,
    "tags": [
        {"name": "tree"},
        {"name": "bark"},
        {"name": "texture"},
        {"name": "wood"},
        {"name": "nature"},
        {"name": "pattern"},
        {"name": "rough"},
        {"name": "surface"},
        {"name": "brown"},
        {"name": "old"},
        {"name": "background"},
        {"name": "trunk"},
        {"name": "natural"},
        {"name": "forest"},
        {"name": "detail"},
        {"name": "lumber"},
        {"name": "weathered"},
        {"name": "timber"},
        {"name": "stump"},
        {"name": "closeup"},
        {"name": "root"},
    ],
    "attribution": None,
    "fields_matched": [],
    "mature": False,
    "height": None,
    "width": None,
    "thumbnail": f"{origin}/v1/images/{identifier}/thumb/",
    "detail_url": f"{origin}/v1/images/{identifier}/",
    "related_url": f"{origin}/v1/images/{identifier}/related/",
}

detailed_image = base_image | {
    "attribution": '"Tree Bark Photo" by Tim Sullivan is marked with CC0 1.0. To view the terms, visit https://creativecommons.org/publicdomain/zero/1.0/.',  # noqa: E501
    "height": 4016,
    "filesize": 896128,
    "filetype": "jpg",
    "width": 6016,
    "mature": None,
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
                "mature": False,
                "height": None,
                "width": None,
                "attribution": None,
                "filesize": None,
                "filetype": None,
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

image_detail_200_example = {"application/json": detailed_image}

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
        "width": 6016,
        "height": 4016,
        "title": "Tree Bark Photo",
        "author_name": "Tim Sullivan",
        "author_url": "https://www.secretagencygroup.com",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
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
