image_search_200_example = {
    "application/json": {
        "result_count": 77,
        "page_count": 77,
        "page_size": 1,
        "results": [
            {
                "title": "File:Well test separator.svg",
                "id": "36537842-b067-4ca0-ad67-e00ff2e06b2d",
                "creator": "en:User:Oil&GasIndustry",
                "creator_url": "https://en.wikipedia.org/wiki/User:Oil%26GasIndustry",
                "url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Well_test_separator.svg",
                "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                "provider": "wikimedia",
                "source": "wikimedia",
                "license": "by",
                "license_version": "3.0",
                "license_url": "https://creativecommons.org/licenses/by/3.0",
                "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=26229990",
                "detail_url": "http://api.creativecommons.engineering/v1/images/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                "fields_matched": [
                    "description",
                    "title"
                ]
            }
        ]
    },
}

image_search_400_example = {
    "application/json": {
        "error": "InputError",
        "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",
        "fields": [
            "license"
        ]
    }
}

recommendations_images_read_200_example = {
    "application/json": {
        "result_count": 10000,
        "page_count": 0,
        "results": [
            {
                "title": "exam tactics",
                "id": "610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                "creator": "Sean MacEntee",
                "creator_url": "https://www.flickr.com/photos/18090920@N07",
                "tags": [
                    {
                        "name": "exam"
                    },
                    {
                        "name": "tactics"
                    }
                ],
                "url": "https://live.staticflickr.com/4065/4459771899_07595dc42e.jpg",
                "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                "provider": "flickr",
                "source": "flickr",
                "license": "by",
                "license_version": "2.0",
                "license_url": "https://creativecommons.org/licenses/by/2.0/",
                "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/4459771899",
                "detail_url": "http://api.creativecommons.engineering/v1/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d"
            }
        ]
    }
}

recommendations_images_read_404_example = {
    "application/json": {
        "detail": "An internal server error occurred."
    }
}

image_detail_200_example = {
    "application/json": {
        "title": "exam test",
        "id": "7c829a03-fb24-4b57-9b03-65f43ed19395",
        "creator": "Sean MacEntee",
        "creator_url": "https://www.flickr.com/photos/18090920@N07",
        "tags": [
            {
                "name": "exam"
            },
            {
                "name": "test"
            }
        ],
        "url": "https://live.staticflickr.com/5122/5264886972_3234d62748.jpg",
        "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/7c829a03-fb24-4b57-9b03-65f43ed19395",
        "provider": "flickr",
        "source": "flickr",
        "license": "by",
        "license_version": "2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/5264886972",
        "detail_url": "http://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395",
        "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/7c829a03-fb24-4b57-9b03-65f43ed19395",
        "height": 167,
        "width": 500,
        "attribution": "\"exam test\" by Sean MacEntee is licensed under CC-BY 2.0. To view a copy of this license, visit https://creativecommons.org/licenses/by/2.0/"
    }
}

image_detail_404_example = {
    "application/json": {
        "detail": "Not found."
    }
}

oembed_list_200_example = {
    "application/json": {
        "version": 1,
        "type": "photo",
        "width": 500,
        "height": 167,
        "title": "exam test",
        "author_name": "Sean MacEntee",
        "author_url": "https://www.flickr.com/photos/18090920@N07",
        "license_url": "https://creativecommons.org/licenses/by/2.0/"
    }
}

oembed_list_404_example = {
    "application/json": {
        "detail": "An internal server error occurred."
    }
}

images_report_create_201_example = {
    "application/json": {
        "reason": "mature",
        "identifier": "7c829a03-fb24-4b57-9b03-65f43ed19395",
        "description": "This image contains sensitive content"
    }
}
