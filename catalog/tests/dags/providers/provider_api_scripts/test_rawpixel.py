import pytest

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from common.licenses import LicenseInfo
from common.loader.provider_details import ImageCategory
from providers.provider_api_scripts.rawpixel import RawpixelDataIngester


_license_info = (
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    None,
)
license_info = LicenseInfo(*_license_info)
rwp = RawpixelDataIngester()
rwp.api_key = "PREDICTABLE-KEY"


_get_resource_json = make_resource_json_func("rawpixel")


@pytest.mark.parametrize(
    "query_params, expected",
    [
        # Empty params
        ({}, "j5VDmEme7JqzMkKAxNfjWb6EaVtIpLq4N2QnYIHZvWg"),
        # One item
        ({"foo": "bar"}, "ZenXVF0pAhfm9EzlAsvw-REsQ27nQQ5mtxmSu4upmHo"),
        # Multiple items
        (
            {"foo": "bar", "crimothy": "roberts"},
            "rSz4Ou1ZZFY57z5Ff7AHxZqwZW_PsgOsN9ksTmpbWIM",
        ),
        # Multiple items of different types
        ({"foo": "bar", "dogs": 12}, "qWEHU7OsSfSFcNsqS9OkHWMDWe_33DBxMR9ULOLrLSw"),
        (
            {"foo": "bar", "sentence": "to+be+or+not+to+be"},
            "aJccI57xaj_pH_xUcD208ZKO_lWne0c2KsjSO15qI-I",
        ),
        (
            {"foo": "bar", "sentence": "to be or not to be"},
            "jbW0P2Oi2LL-BLvRsGAydF7VGlFOvWQFMSbkJFX6LQo",
        ),
        # Multiple items with list
        (
            {"foo": "bar", "favorites": ["chocolate", "video games", "cats"]},
            "FM_kVUym-GonOgfZAeNuswEQLZas3BOOvkTXvax_mTw",
        ),
    ],
)
def test_get_signature(query_params, expected):
    actual = rwp._get_signature(query_params)
    assert actual == expected


def test_get_next_query_params_empty():
    actual = rwp.get_next_query_params({})
    actual.pop("s")
    assert actual == {
        "tags": "$publicdomain",
        "page": 1,
        "pagesize": 100,
    }


def test_get_next_query_params_increments_page_size():
    actual = rwp.get_next_query_params({"foo": "bar", "page": 5})
    actual.pop("s")
    assert actual == {"foo": "bar", "page": 6}


@pytest.mark.parametrize(
    "data, expected",
    [
        # No data
        ({}, None),
        # Missing filter passes through
        ({"style_uri": "nothing_to_format"}, "nothing_to_format"),
        # Happy path
        (
            {"style_uri": "string_to_format: {}"},
            f"string_to_format: {rwp.full_size_option}",
        ),
    ],
)
def test_get_image_url(data, expected):
    actual = rwp._get_image_url(data, rwp.full_size_option)
    assert actual == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        # Empty case
        ({}, (None, None)),
        # Happy path normal fields
        ({"width": 500, "height": 600}, (500, 600)),
        # Happy path display image fields
        ({"display_image_width": 500, "display_image_height": 600}, (500, 600)),
        # One field is 0 but data is still present
        ({"width": 0, "height": 600}, (0, 600)),
        # Fields conflict so max is chosen
        ({"width": 500, "display_image_width": 700, "height": 600}, (700, 600)),
    ],
)
def test_get_image_properties(data, expected):
    actual = rwp._get_image_properties(data)
    assert actual == expected


@pytest.mark.parametrize(
    "title, expected",
    [
        (
            "Bull elk searches for food | Free Photo - rawpixel",
            "Bull elk searches for food",
        ),
        (
            "Desktop wallpaper summer beach landscape, | Free Photo - rawpixel",
            "Desktop wallpaper summer beach landscape",
        ),
        (
            "Japanese autumn tree color drawing. | Free Photo - rawpixel",
            "Japanese autumn tree color drawing",
        ),
        (
            "Open hand, palm reading. Original | Free Photo Illustration - rawpixel",
            "Open hand, palm reading",
        ),
        (
            "Claude Monet's The Magpie (1868&ndash;1869) | Free Photo Illustration - rawpixel",
            "Claude Monet's The Magpie (1868–1869)",
        ),
        ("Red poppy field. Free public | Free Photo - rawpixel", "Red poppy field"),
        ("Free public domain CC0 photo. | Free Photo - rawpixel", None),
        (
            "Floral glasses. Free public domain | Free Photo - rawpixel",
            "Floral glasses",
        ),
        (
            "Claude Monet's The Cliffs at &Eacute;tretat | Free Photo Illustration - rawpixel",
            "Claude Monet's The Cliffs at Étretat",
        ),
    ],
)
def test_get_title(title, expected):
    metadata = {"title": title}
    actual = rwp._get_title(metadata)
    assert actual == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        # Empty cases
        ({}, None),
        ({"artist_names": ""}, None),
        # Name without suffix
        ({"artist_names": "Monet"}, "Monet"),
        # Name with spaces
        ({"artist_names": "   Monet    "}, "Monet"),
        # Name with suffix
        ({"artist_names": "Monet (Source)"}, "Monet"),
    ],
)
def test_get_source(data, expected):
    actual = rwp._get_creator(data)
    assert actual == expected


EXAMPLE_KEYWORDS = [
    # Digitized art
    [
        "floral",
        "flower",
        "flowers public domain",
        "illustration",
        "ornament",
        "public domain art",
        "public domain",
        "victorian",
        "vintage flowers",
        "vintage illustration public domain",
        "vintage illustrations",
        "vintage",
    ],
    # Illustration
    [
        "animal art",
        "animal illustrations",
        "bengal tiger",
        "clip art public domain",
        "clipart",
        "face",
        "orange",
        "public domain animal",
        "public domain tiger",
        "tiger face",
        "tiger",
        "wildlife",
    ],
    # Photograph
    [
        "animal photos",
        "animal",
        "animals public domain",
        "beagle",
        "dog",
        "fashion dog",
        "hat dog",
        "image",
        "photo",
        "public domain dog",
        "public domain fashion",
        "public domain",
    ],
]


@pytest.mark.parametrize(
    "keywords, expected",
    zip(
        EXAMPLE_KEYWORDS,
        (
            {
                "floral",
                "flower",
                "flowers public domain",
                "illustration",
                "ornament",
                "public domain art",
                "public domain",
                "victorian",
                "vintage flowers",
                "vintage illustration public domain",
                "vintage illustrations",
                "vintage",
            },
            {
                "animal art",
                "animal illustrations",
                "bengal tiger",
                "clip art public domain",
                "clipart",
                "face",
                "orange",
                "public domain animal",
                "public domain tiger",
                "tiger face",
                "tiger",
                "wildlife",
            },
            {
                "animal photos",
                "animal",
                "animals public domain",
                "beagle",
                "dog",
                "fashion dog",
                "hat dog",
                "image",
                "photo",
                "public domain dog",
                "public domain fashion",
                "public domain",
            },
        ),
    ),
)
def test_get_tags(keywords, expected):
    actual = rwp._get_tags({"popular_keywords": keywords})
    assert actual == expected


@pytest.mark.parametrize(
    "keywords, expected",
    zip(
        [*EXAMPLE_KEYWORDS, []],
        [
            ImageCategory.DIGITIZED_ARTWORK,
            ImageCategory.ILLUSTRATION,
            ImageCategory.PHOTOGRAPH,
            None,
        ],
    ),
)
def test_get_category(keywords, expected):
    actual = rwp._get_category({"popular_keywords": keywords})
    assert actual == expected


def test_get_record_data():
    data = _get_resource_json("public_domain_response.json")
    actual = rwp.get_record_data(data["results"][0])
    assert actual == {
        "category": None,
        "creator": "National Park Service",
        "filetype": "jpg",
        "foreign_identifier": 4032668,
        "foreign_landing_url": "https://www.rawpixel.com/image/4032668/photo-image-background-nature-mountain",  # noqa
        "height": 5515,
        "url": "https://images.rawpixel.com/editor_1024/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA1L2ZsNDY0NDU5OTQ2MjQtaW1hZ2Uta3UyY21zcjUuanBn.jpg",  # noqa,
        "thumbnail_url": "https://images.rawpixel.com/image_600/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA1L2ZsNDY0NDU5OTQ2MjQtaW1hZ2Uta3UyY21zcjUuanBn.jpg",  # noqa
        "license_info": LicenseInfo(
            license="cc0",
            version="1.0",
            url="https://creativecommons.org/publicdomain/zero/1.0/",
            raw_url="https://creativecommons.org/publicdomain/zero/1.0/",
        ),
        "meta_data": {
            "description": "Bull elk searches for food beneath the snow. Frank. Original public domain image from Flickr",  # noqa
            "download_count": 0,
        },
        "raw_tags": {
            "animal",
            "background",
            "deer",
            "elk",
            "national park",
            "nature background",
            "public domain",
            "snow",
            "sunset",
            "wildlife",
            "winter",
            "yellowstone",
        },
        "title": "Bull elk searches for food",
        "width": 8272,
    }


def test_get_record_data_returns_none_if_missing_required_values():
    data = _get_resource_json("public_domain_response.json")["results"][0]
    data["metadata"]["licenseUrl"] = None
    actual = rwp.get_record_data(data)

    assert actual is None
